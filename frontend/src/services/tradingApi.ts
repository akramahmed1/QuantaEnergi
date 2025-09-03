/**
 * Comprehensive Trading API Service for QuantaEnergi Platform
 * Integrates with all backend ETRM/CTRM features
 */

// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Generic API request function with error handling
async function apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
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

    return await response.json();
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
  details: Record<string, any>;
  timestamp: string;
}

export async function captureTrade(tradeData: TradeCreate): Promise<TradeResponse> {
  return apiRequest<TradeResponse>('/api/v1/trade-lifecycle/capture', {
    method: 'POST',
    body: JSON.stringify(tradeData)
  });
}

export async function validateTrade(tradeId: string): Promise<TradeStatusResponse> {
  return apiRequest<TradeStatusResponse>(`/api/v1/trade-lifecycle/${tradeId}/validate`, {
    method: 'POST'
  });
}

export async function generateConfirmation(tradeId: string): Promise<{ confirmation_id: string; status: string }> {
  return apiRequest(`/api/v1/trade-lifecycle/${tradeId}/confirm`, {
    method: 'POST'
  });
}

export async function allocateTrade(tradeId: string, allocationData: Record<string, any>): Promise<{ allocation_id: string; status: string }> {
  return apiRequest(`/api/v1/trade-lifecycle/${tradeId}/allocate`, {
    method: 'POST',
    body: JSON.stringify(allocationData)
  });
}

export async function processSettlement(tradeId: string, settlementData: Record<string, any>): Promise<{ settlement_id: string; status: string }> {
  return apiRequest(`/api/v1/trade-lifecycle/${tradeId}/settle`, {
    method: 'POST',
    body: JSON.stringify(settlementData)
  });
}

export async function generateInvoice(tradeId: string): Promise<{ invoice_id: string; status: string }> {
  return apiRequest(`/api/v1/trade-lifecycle/${tradeId}/invoice`, {
    method: 'POST'
  });
}

export async function processPayment(tradeId: string, paymentData: Record<string, any>): Promise<{ payment_id: string; status: string }> {
  return apiRequest(`/api/v1/trade-lifecycle/${tradeId}/payment`, {
    method: 'POST',
    body: JSON.stringify(paymentData)
  });
}

export async function getTradeStatus(tradeId: string): Promise<TradeStatusResponse> {
  return apiRequest<TradeStatusResponse>(`/api/v1/trade-lifecycle/${tradeId}/status`);
}

export async function getUserTrades(): Promise<TradeResponse[]> {
  return apiRequest<TradeResponse[]>('/api/v1/trade-lifecycle/');
}

export async function cancelTrade(tradeId: string): Promise<{ message: string }> {
  return apiRequest(`/api/v1/trade-lifecycle/${tradeId}`, {
    method: 'DELETE'
  });
}

// ============================================================================
// CREDIT MANAGEMENT API
// ============================================================================

export interface CreditLimit {
  counterparty_id: string;
  limit_amount: number;
  currency: string;
  risk_rating: string;
  expiry_date: string;
  terms?: Record<string, any>;
}

export interface CreditExposure {
  counterparty_id: string;
  current_exposure: number;
  available_credit: number;
  utilization_percentage: number;
  risk_level: string;
  last_updated: string;
}

export async function setCreditLimit(creditLimit: CreditLimit): Promise<{ success: boolean; message: string }> {
  return apiRequest('/api/v1/credit/limits', {
    method: 'POST',
    body: JSON.stringify(creditLimit)
  });
}

export async function getCreditLimit(counterpartyId: string): Promise<{ success: boolean; data: CreditLimit }> {
  return apiRequest(`/api/v1/credit/limits/${counterpartyId}`);
}

export async function getAllCreditLimits(): Promise<{ success: boolean; data: CreditLimit[] }> {
  return apiRequest('/api/v1/credit/limits');
}

export async function calculateExposure(counterpartyId: string, positions: any[]): Promise<{ success: boolean; data: CreditExposure }> {
  return apiRequest(`/api/v1/credit/exposure/calculate?counterparty_id=${counterpartyId}`, {
    method: 'POST',
    body: JSON.stringify(positions)
  });
}

export async function getExposure(counterpartyId: string): Promise<{ success: boolean; data: CreditExposure }> {
  return apiRequest(`/api/v1/credit/exposure/${counterpartyId}`);
}

export async function checkCreditAvailability(counterpartyId: string, tradeAmount: number): Promise<{ success: boolean; data: { available: boolean; remaining_credit: number } }> {
  return apiRequest(`/api/v1/credit/availability/check?counterparty_id=${counterpartyId}&trade_amount=${tradeAmount}`, {
    method: 'POST'
  });
}

export async function getCreditAvailability(counterpartyId: string): Promise<{ success: boolean; data: { available_credit: number; utilization: number } }> {
  return apiRequest(`/api/v1/credit/availability/${counterpartyId}`);
}

export async function generateCreditReport(): Promise<{ success: boolean; data: { total_counterparties: number; total_exposure: number } }> {
  return apiRequest('/api/v1/credit/reports/generate', {
    method: 'POST'
  });
}

export async function getCreditDashboard(): Promise<{ success: boolean; data: { total_counterparties: number; total_exposure: number; risk_distribution: Record<string, number> } }> {
  return apiRequest('/api/v1/credit/dashboard');
}

// ============================================================================
// REGULATORY COMPLIANCE API
// ============================================================================

export interface ComplianceReport {
  region: string;
  regulation_type: string;
  compliance_status: boolean;
  requirements_met: string[];
  requirements_missing: string[];
  risk_level: string;
  last_check: string;
}

export async function generateComplianceReport(region: string, regulationType: string): Promise<{ success: boolean; message: string }> {
  return apiRequest(`/api/v1/compliance/reports/generate?region=${region}&regulation_type=${regulationType}`, {
    method: 'POST'
  });
}

export async function generateBulkComplianceReports(regions: string[]): Promise<{ success: boolean; message: string }> {
  return apiRequest(`/api/v1/compliance/reports/bulk?regions=${regions.join(',')}`, {
    method: 'POST'
  });
}

export async function anonymizeComplianceData(data: Record<string, any>): Promise<{ success: boolean; data: Record<string, any> }> {
  return apiRequest('/api/v1/compliance/data/anonymize', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

export async function getComplianceRegions(): Promise<{ success: boolean; data: string[] }> {
  return apiRequest('/api/v1/compliance/regions');
}

export async function getComplianceStatus(): Promise<{ success: boolean; data: Record<string, { compliant: boolean; score: number }> }> {
  return apiRequest('/api/v1/compliance/status');
}

export async function getComplianceDashboard(): Promise<{ success: boolean; data: { total_regions: number; compliance_overview: Record<string, any> } }> {
  return apiRequest('/api/v1/compliance/dashboard');
}

export async function validateComplianceRequirements(region: string, regulationType: string): Promise<{ success: boolean; data: { compliant: boolean; score: number } }> {
  return apiRequest(`/api/v1/compliance/validation/check?region=${region}&regulation_type=${regulationType}`, {
    method: 'POST'
  });
}

export async function getComplianceHistory(): Promise<{ success: boolean; data: ComplianceReport[] }> {
  return apiRequest('/api/v1/compliance/history');
}

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
  historical_returns?: number[];
}

export interface RiskMetrics {
  var_95: number;
  var_99: number;
  expected_shortfall: number;
  stress_test_results: Record<string, any>;
  correlation_matrix: Record<string, any>;
  calculated_at: string;
}

export async function calculateVaRMonteCarlo(
  portfolioData: PortfolioData,
  confidenceLevel: number = 0.95,
  timeHorizon: number = 1,
  numSimulations: number = 10000
): Promise<{ success: boolean; message: string }> {
  return apiRequest('/api/v1/risk-analytics/var/monte-carlo', {
    method: 'POST',
    body: JSON.stringify(portfolioData),
    headers: {
      'Content-Type': 'application/json',
    }
  });
}

export async function calculateVaRParametric(
  portfolioData: PortfolioData,
  confidenceLevel: number = 0.95,
  timeHorizon: number = 1
): Promise<{ success: boolean; data: { var_value: number } }> {
  return apiRequest('/api/v1/risk-analytics/var/parametric', {
    method: 'POST',
    body: JSON.stringify(portfolioData),
    headers: {
      'Content-Type': 'application/json',
    }
  });
}

export async function calculateVaRHistorical(
  portfolioData: PortfolioData,
  confidenceLevel: number = 0.95,
  timeHorizon: number = 1,
  historicalPeriod: number = 252
): Promise<{ success: boolean; data: { var_value: number } }> {
  return apiRequest('/api/v1/risk-analytics/var/historical', {
    method: 'POST',
    body: JSON.stringify(portfolioData),
    headers: {
      'Content-Type': 'application/json',
    }
  });
}

export async function stressTestPortfolio(
  portfolioData: PortfolioData,
  stressScenarios: Array<{ name: string; type: string; shock_factor?: number; spike_factor?: number }>
): Promise<{ success: boolean; message: string }> {
  return apiRequest('/api/v1/risk-analytics/stress-test', {
    method: 'POST',
    body: JSON.stringify({ portfolio_data: portfolioData, stress_scenarios: stressScenarios })
  });
}

export async function calculateExpectedShortfall(
  portfolioData: PortfolioData,
  confidenceLevel: number = 0.95,
  timeHorizon: number = 1
): Promise<{ success: boolean; message: string }> {
  return apiRequest('/api/v1/risk-analytics/expected-shortfall', {
    method: 'POST',
    body: JSON.stringify(portfolioData),
    headers: {
      'Content-Type': 'application/json',
    }
  });
}

export async function performScenarioAnalysis(
  portfolioData: PortfolioData,
  scenarios: Array<{ name: string; type: string; shock_factor?: number; spike_factor?: number }>
): Promise<{ success: boolean; data: { scenarios_analyzed: number; results: Record<string, any> } }> {
  return apiRequest('/api/v1/risk-analytics/scenario-analysis', {
    method: 'POST',
    body: JSON.stringify({ portfolio_data: portfolioData, scenarios })
  });
}

export async function generateRiskReport(
  portfolioData: PortfolioData,
  reportType: string = 'comprehensive',
  includeScenarios: boolean = true
): Promise<{ success: boolean; message: string }> {
  return apiRequest('/api/v1/risk-analytics/risk-report', {
    method: 'POST',
    body: JSON.stringify(portfolioData),
    headers: {
      'Content-Type': 'application/json',
    }
  });
}

export async function getRiskMetrics(): Promise<{ success: boolean; data: RiskMetrics }> {
  return apiRequest('/api/v1/risk-analytics/risk-metrics');
}

export async function getRiskDashboard(): Promise<{ success: boolean; data: { total_portfolios: number; risk_overview: Record<string, any> } }> {
  return apiRequest('/api/v1/risk-analytics/dashboard');
}

export async function runMonteCarloSimulation(simulationParams: {
  positions: Array<{ commodity: string; notional_value: number; expected_return: number; volatility: number }>;
  market_data: Record<string, any>;
  correlations: Record<string, any>;
  num_simulations: number;
  time_horizon: number;
}): Promise<{ success: boolean; data: { simulation_id: string } }> {
  return apiRequest('/api/v1/risk-analytics/simulation/monte-carlo', {
    method: 'POST',
    body: JSON.stringify(simulationParams)
  });
}

export async function getSimulationStatus(simulationId: string): Promise<{ success: boolean; data: { status: string } }> {
  return apiRequest(`/api/v1/risk-analytics/simulation/${simulationId}/status`);
}

export async function getSimulationResults(simulationId: string): Promise<{ success: boolean; data: { var_95: number; expected_shortfall: number } }> {
  return apiRequest(`/api/v1/risk-analytics/simulation/${simulationId}/results`);
}

// ============================================================================
// ALGORITHMIC TRADING API
// ============================================================================

export interface AlgoStrategyCreate {
  strategy_name: string;
  strategy_type: string;
  parameters: Record<string, any>;
  risk_limits: Record<string, number>;
  islamic_compliant: boolean;
  execution_mode: string;
}

export interface AlgoStrategyResponse {
  strategy_id: string;
  strategy_name: string;
  strategy_type: string;
  parameters: Record<string, any>;
  risk_limits: Record<string, number>;
  islamic_compliant: boolean;
  execution_mode: string;
  status: string;
  created_at: string;
}

export async function executeAlgorithm(algoSpec: AlgoStrategyCreate): Promise<{ status: string; data: { execution_id: string; strategy: string } }> {
  return apiRequest('/api/v1/options/algo/execute', {
    method: 'POST',
    body: JSON.stringify(algoSpec)
  });
}

export async function calculateVWAP(orders: Array<{ price: number; volume: number }>, timePeriod: string = '1D'): Promise<{ status: string; data: { vwap: number; total_volume: number } }> {
  return apiRequest('/api/v1/options/algo/vwap', {
    method: 'POST',
    body: JSON.stringify(orders),
    headers: {
      'Content-Type': 'application/json',
    }
  });
}

export async function executeTWAPStrategy(twapParams: {
  total_quantity: number;
  duration_minutes: number;
  slice_interval: number;
  commodity: string;
  execution_type: string;
}): Promise<{ status: string; data: { strategy_id: string; strategy_type: string; execution_slices: any[] } }> {
  return apiRequest('/api/v1/options/algo/twap', {
    method: 'POST',
    body: JSON.stringify(twapParams)
  });
}

export async function optimizeOrderSizing(
  marketData: Record<string, any>,
  targetVolume: number,
  riskParams: Record<string, any>
): Promise<{ status: string; data: { optimization_id: string; optimal_slice_size: number } }> {
  return apiRequest('/api/v1/options/algo/optimize-sizing', {
    method: 'POST',
    body: JSON.stringify({ market_data: marketData, risk_params: riskParams }),
    headers: {
      'Content-Type': 'application/json',
    }
  });
}

export async function monitorExecutionQuality(executionId: string): Promise<{ status: string; data: { execution_id: string; quality_score: number } }> {
  return apiRequest(`/api/v1/options/algo/execution-quality/${executionId}`);
}

export async function getStrategyPerformance(strategyType: string, timePeriod: string = '1M'): Promise<{ status: string; data: { strategy_type: string; total_trades: number; win_rate: number } }> {
  return apiRequest(`/api/v1/options/algo/performance/${strategyType}?time_period=${timePeriod}`);
}

export async function validateAlgoStrategy(strategyData: Record<string, any>): Promise<{ status: string; data: { islamic_compliant: boolean; compliance_score: number } }> {
  return apiRequest('/api/v1/options/islamic/validate-algo', {
    method: 'POST',
    body: JSON.stringify(strategyData)
  });
}

export async function checkExecutionEthics(executionData: Record<string, any>): Promise<{ status: string; data: { ethical_execution: boolean; fairness_score: number } }> {
  return apiRequest('/api/v1/options/islamic/check-execution-ethics', {
    method: 'POST',
    body: JSON.stringify(executionData)
  });
}

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

export interface OptionResponse {
  option_id: string;
  option_type: string;
  underlying: string;
  strike_price: number;
  expiry_date: string;
  quantity: number;
  premium: number;
  greeks: Record<string, number>;
  islamic_compliant: boolean;
  created_at: string;
}

export async function priceOption(optionSpec: OptionCreate): Promise<{ status: string; data: Record<string, any> }> {
  return apiRequest('/api/v1/options/price', {
    method: 'POST',
    body: JSON.stringify(optionSpec)
  });
}

export async function calculateArbunPremium(
  underlyingPrice: number,
  strikePrice: number,
  timeToExpiry: number,
  volatility: number
): Promise<{ status: string; data: Record<string, any> }> {
  return apiRequest('/api/v1/options/arbun-premium', {
    method: 'POST',
    body: JSON.stringify({
      underlying_price: underlyingPrice,
      strike_price: strikePrice,
      time_to_expiry: timeToExpiry,
      volatility: volatility
    })
  });
}

export async function validateIslamicOption(optionData: Record<string, any>): Promise<{ status: string; data: Record<string, any> }> {
  return apiRequest('/api/v1/options/validate-islamic', {
    method: 'POST',
    body: JSON.stringify(optionData)
  });
}

export async function executeOptionTrade(optionId: string, executionParams: Record<string, any>): Promise<{ status: string; data: Record<string, any> }> {
  return apiRequest('/api/v1/options/execute', {
    method: 'POST',
    body: JSON.stringify({ option_id: optionId, execution_params: executionParams })
  });
}

export async function getOptionPortfolio(userId: string): Promise<{ status: string; data: Record<string, any> }> {
  return apiRequest(`/api/v1/options/portfolio/${userId}`);
}

// ============================================================================
// STRUCTURED PRODUCTS API
// ============================================================================

export interface StructuredProductCreate {
  product_type: string;
  underlying: string;
  notional_amount: number;
  maturity_date: string;
  payoff_structure: Record<string, any>;
  islamic_compliant: boolean;
  risk_parameters: Record<string, any>;
}

export async function createStructuredProduct(productSpec: StructuredProductCreate): Promise<{ status: string; data: Record<string, any> }> {
  return apiRequest('/api/v1/options/structured/create', {
    method: 'POST',
    body: JSON.stringify(productSpec)
  });
}

export async function priceStructuredProduct(productId: string, marketData: Record<string, any>): Promise<{ status: string; data: Record<string, any> }> {
  return apiRequest('/api/v1/options/structured/price', {
    method: 'POST',
    body: JSON.stringify({ product_id: productId, market_data: marketData })
  });
}

export async function calculatePayoffProfile(productId: string, scenarios: Record<string, any>[]): Promise<{ status: string; data: Record<string, any> }> {
  return apiRequest('/api/v1/options/structured/payoff-profile', {
    method: 'POST',
    body: JSON.stringify({ product_id: productId, scenarios })
  });
}

export async function validateStructuredIslamic(productData: Record<string, any>): Promise<{ status: string; data: Record<string, any> }> {
  return apiRequest('/api/v1/options/structured/validate-islamic', {
    method: 'POST',
    body: JSON.stringify(productData)
  });
}

export async function executeStructuredTrade(productId: string, executionParams: Record<string, any>): Promise<{ status: string; data: Record<string, any> }> {
  return apiRequest('/api/v1/options/structured/execute', {
    method: 'POST',
    body: JSON.stringify({ product_id: productId, execution_params: executionParams })
  });
}

export async function getStructuredPortfolio(userId: string): Promise<{ status: string; data: Record<string, any> }> {
  return apiRequest(`/api/v1/options/structured/portfolio/${userId}`);
}

// ============================================================================
// ISLAMIC COMPLIANCE VALIDATION API
// ============================================================================

export async function validateArbunStructure(optionData: Record<string, any>): Promise<{ status: string; data: Record<string, any> }> {
  return apiRequest('/api/v1/options/islamic/validate-arbun', {
    method: 'POST',
    body: JSON.stringify(optionData)
  });
}

export async function checkGhararLevels(optionData: Record<string, any>): Promise<{ status: string; data: Record<string, any> }> {
  return apiRequest('/api/v1/options/islamic/check-gharar', {
    method: 'POST',
    body: JSON.stringify(optionData)
  });
}

export async function validateMurabahaStructure(productData: Record<string, any>): Promise<{ status: string; data: Record<string, any> }> {
  return apiRequest('/api/v1/options/islamic/validate-murabaha', {
    method: 'POST',
    body: JSON.stringify(productData)
  });
}

export async function checkProfitSharingMechanism(productData: Record<string, any>): Promise<{ status: string; data: Record<string, any> }> {
  return apiRequest('/api/v1/options/islamic/check-profit-sharing', {
    method: 'POST',
    body: JSON.stringify(productData)
  });
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

export function formatCurrency(amount: number, currency: string = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
}

export function formatPercentage(value: number): string {
  return `${(value * 100).toFixed(2)}%`;
}

export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function calculatePnL(currentPrice: number, avgPrice: number, quantity: number): number {
  return (currentPrice - avgPrice) * quantity;
}

export function calculatePnLPercentage(currentPrice: number, avgPrice: number): number {
  return ((currentPrice - avgPrice) / avgPrice) * 100;
}
