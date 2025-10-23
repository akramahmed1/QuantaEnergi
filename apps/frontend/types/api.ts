/**
 * TypeScript types generated from backend Pydantic models
 * Provides strict typing for all API interactions
 */

// Base types
export interface BaseEntity {
  id: string;
  created_at: string;
  updated_at?: string;
}

export interface TenantEntity extends BaseEntity {
  tenant_id: string;
}

// Enums
export enum TradeStatus {
  PENDING = 'pending',
  CAPTURED = 'captured',
  VALIDATED = 'validated',
  CONFIRMED = 'confirmed',
  ALLOCATED = 'allocated',
  SETTLED = 'settled',
  INVOICED = 'invoiced',
  PAID = 'paid',
  CANCELLED = 'cancelled',
  REJECTED = 'rejected',
}

export enum TradeType {
  SPOT = 'spot',
  FORWARD = 'forward',
  FUTURES = 'futures',
  OPTIONS = 'options',
  SWAP = 'swap',
  CREDIT_DEFAULT_SWAP = 'credit_default_swap',
  INTEREST_RATE_SWAP = 'interest_rate_swap',
  CURRENCY_SWAP = 'currency_swap',
}

export enum CommodityType {
  CRUDE_OIL = 'crude_oil',
  NATURAL_GAS = 'natural_gas',
  ELECTRICITY = 'electricity',
  CARBON_CREDITS = 'carbon_credits',
  RENEWABLE_ENERGY = 'renewable_energy',
  COAL = 'coal',
  URANIUM = 'uranium',
}

export enum RiskLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

export enum ComplianceRegion {
  US = 'us',
  UK = 'uk',
  EU = 'eu',
  MIDDLE_EAST = 'middle_east',
  GUYANA = 'guyana',
  GLOBAL = 'global',
}

export enum UserRole {
  ADMIN = 'admin',
  TRADER = 'trader',
  RISK_MANAGER = 'risk_manager',
  COMPLIANCE_OFFICER = 'compliance_officer',
  VIEWER = 'viewer',
}

export enum Currency {
  USD = 'USD',
  EUR = 'EUR',
  GBP = 'GBP',
  AED = 'AED',
  SAR = 'SAR',
  GYD = 'GYD',
}

// Response types
export interface SuccessResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  timestamp: string;
}

export interface ErrorResponse {
  success: boolean;
  error: {
    id: string;
    timestamp: string;
    message: string;
    code: string;
    details: Record<string, any>;
    path: string;
    method: string;
    user_agent: string;
    ip_address?: string;
    status_code: number;
  };
  request_id: string;
  correlation_id: string;
}

export interface PaginationParams {
  page: number;
  page_size: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

// Trade related types
export interface Trade extends TenantEntity {
  trade_id: string;
  trade_type: TradeType;
  commodity_type: CommodityType;
  quantity: number;
  price: number;
  currency: Currency;
  counterparty: string;
  trade_date: string;
  settlement_date: string;
  status: TradeStatus;
  region: ComplianceRegion;
  is_sharia_compliant: boolean;
  risk_level: RiskLevel;
  created_by: string;
  validated_by?: string;
  confirmed_by?: string;
  allocated_by?: string;
  settled_by?: string;
  invoiced_by?: string;
  paid_by?: string;
  cancellation_reason?: string;
  rejection_reason?: string;
  metadata: Record<string, any>;
}

export interface TradeCreateRequest {
  trade_type: TradeType;
  commodity_type: CommodityType;
  quantity: number;
  price: number;
  currency: Currency;
  counterparty: string;
  trade_date: string;
  settlement_date: string;
  region: ComplianceRegion;
  is_sharia_compliant: boolean;
  metadata?: Record<string, any>;
}

export interface TradeUpdateRequest {
  quantity?: number;
  price?: number;
  counterparty?: string;
  settlement_date?: string;
  is_sharia_compliant?: boolean;
  metadata?: Record<string, any>;
}

// Risk Analytics types
export interface VaRCalculation {
  portfolio_id: string;
  confidence_level: number;
  time_horizon: number;
  var_value: number;
  expected_shortfall: number;
  calculation_method: 'monte_carlo' | 'parametric' | 'historical';
  calculation_date: string;
  underlying_data: {
    positions: Array<{
      commodity: CommodityType;
      quantity: number;
      price: number;
    }>;
    market_data: Record<string, any>;
  };
}

export interface StressTestScenario {
  scenario_id: string;
  name: string;
  description: string;
  market_shocks: Record<CommodityType, number>;
  correlation_changes: Record<string, number>;
  created_by: string;
  created_at: string;
}

export interface StressTestResult {
  scenario_id: string;
  portfolio_id: string;
  portfolio_value_before: number;
  portfolio_value_after: number;
  loss_amount: number;
  loss_percentage: number;
  worst_case_loss: number;
  calculation_date: string;
}

// Market Data types
export interface MarketPrice {
  commodity: CommodityType;
  price: number;
  change: string;
  change_percentage: number;
  volume: number;
  source: string;
  timestamp: string;
  region: ComplianceRegion;
}

export interface WeatherData {
  location: {
    lat: number;
    lon: number;
  };
  temp: number;
  humidity: number;
  description: string;
  wind_speed: number;
  pressure: number;
  visibility: number;
  timestamp: string;
  source: string;
}

export interface RenewableEnergyData {
  wind: number;
  solar: number;
  hydro: number;
  biomass: number;
  geothermal: number;
  total: number;
  efficiency: number;
  carbon_savings: number;
  timestamp: string;
}

// Portfolio types
export interface PortfolioPosition {
  commodity: CommodityType;
  quantity: number;
  avg_price: number;
  current_price: number;
  market_value: number;
  unrealized_pnl: number;
  weight: number;
}

export interface Portfolio {
  portfolio_id: string;
  user_id: string;
  name: string;
  total_value: number;
  cash: number;
  invested: number;
  daily_change: number;
  daily_change_amount: number;
  monthly_change: number;
  yearly_change: number;
  total_return: number;
  positions: PortfolioPosition[];
  allocation: Record<CommodityType, number>;
  risk_metrics: {
    var_95: number;
    var_99: number;
    sharpe_ratio: number;
    beta: number;
    alpha: number;
  };
  created_at: string;
  updated_at: string;
}

// User and Authentication types
export interface User extends BaseEntity {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  is_active: boolean;
  last_login?: string;
  preferences: UserPreferences;
}

export interface UserPreferences {
  theme: 'light' | 'dark';
  language: string;
  timezone: string;
  currency: Currency;
  notifications: {
    email: boolean;
    push: boolean;
    sms: boolean;
  };
  dashboard_layout: Record<string, any>;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

// Compliance types
export interface ComplianceReport {
  report_id: string;
  report_type: string;
  region: ComplianceRegion;
  period_start: string;
  period_end: string;
  status: 'draft' | 'submitted' | 'approved' | 'rejected';
  data: Record<string, any>;
  generated_by: string;
  generated_at: string;
  submitted_at?: string;
  approved_by?: string;
  approved_at?: string;
  rejection_reason?: string;
}

// ESG types
export interface ESGMetrics {
  overall_esg_score: number;
  environmental_score: number;
  social_score: number;
  governance_score: number;
  carbon_offset: number;
  renewable_ratio: number;
  sustainability_score: number;
  climate_risk_score: number;
  social_impact_score: number;
  governance_quality: number;
  esg_trend: string;
  esg_rank: string;
  carbon_intensity: number;
  water_efficiency: number;
  waste_reduction: number;
  diversity_score: number;
  labor_rights: number;
  board_independence: number;
  executive_compensation: number;
  shareholder_rights: number;
  timestamp: string;
}

// Trading Signals types
export interface TradingSignal {
  id: number;
  signal: 'BUY' | 'SELL' | 'HOLD';
  commodity: CommodityType;
  confidence: number;
  price: number;
  target: number;
  stop_loss: number;
  timeframe: string;
  source: string;
  timestamp: string;
  risk: RiskLevel;
  volume: 'Low' | 'Medium' | 'High';
  trend: 'Bullish' | 'Bearish' | 'Sideways';
  esg_impact: 'Positive' | 'Neutral' | 'Negative';
}

// Forecast types
export interface EnergyForecast {
  commodity: CommodityType;
  forecasts: Array<{
    date: string;
    price: number;
    confidence: number;
    factors: string;
    trend: 'bullish' | 'bearish';
    volatility: number;
  }>;
  summary: {
    start_price: number;
    end_price: number;
    total_change: number;
    percent_change: number;
    avg_volatility: number;
  };
  generated_at: string;
  model: string;
}

// API Client types
export interface ApiClientConfig {
  baseURL: string;
  timeout: number;
  headers: Record<string, string>;
}

export interface ApiRequestConfig {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  url: string;
  data?: any;
  params?: Record<string, any>;
  headers?: Record<string, string>;
}

// WebSocket types
export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
}

export interface WebSocketConfig {
  url: string;
  protocols?: string[];
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}
