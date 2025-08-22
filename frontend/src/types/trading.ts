export interface MarketData {
  symbol: string
  price: number
  change: number
  changePercent: number
  volume: number
  high: number
  low: number
  open: number
  previousClose: number
  timestamp: string
  bid?: number
  ask?: number
  spread?: number
}

export interface Order {
  id: string
  symbol: string
  side: 'buy' | 'sell'
  type: 'market' | 'limit' | 'stop' | 'stop_limit'
  quantity: number
  price?: number
  stopPrice?: number
  status: 'pending' | 'filled' | 'cancelled' | 'rejected' | 'partial'
  filledQuantity: number
  averagePrice: number
  commission: number
  timestamp: string
  userId: string
  accountId: string
  timeInForce: 'GTC' | 'IOC' | 'FOK' | 'DAY'
  orderId?: string
  clientOrderId?: string
}

export interface Position {
  id: string
  symbol: string
  side: 'long' | 'short'
  quantity: number
  averagePrice: number
  currentPrice: number
  marketValue: number
  unrealizedPnL: number
  realizedPnL: number
  totalPnL: number
  margin: number
  leverage: number
  timestamp: string
  userId: string
  accountId: string
}

export interface Portfolio {
  id: string
  userId: string
  accountId: string
  totalValue: number
  cash: number
  margin: number
  availableMargin: number
  usedMargin: number
  unrealizedPnL: number
  realizedPnL: number
  totalPnL: number
  positions: Position[]
  timestamp: string
}

export interface User {
  id: string
  username: string
  email: string
  firstName: string
  lastName: string
  role: 'trader' | 'analyst' | 'risk_manager' | 'compliance_officer' | 'admin'
  permissions: string[]
  isActive: boolean
  lastLogin: string
  createdAt: string
  profile: UserProfile
}

export interface UserProfile {
  avatar?: string
  phone?: string
  country?: string
  timezone?: string
  language?: string
  currency?: string
  riskTolerance: 'low' | 'medium' | 'high'
  tradingExperience: 'beginner' | 'intermediate' | 'advanced'
  preferredMarkets: string[]
  notificationPreferences: NotificationPreferences
}

export interface NotificationPreferences {
  email: boolean
  push: boolean
  sms: boolean
  orderUpdates: boolean
  priceAlerts: boolean
  riskAlerts: boolean
  newsUpdates: boolean
}

export interface TradingSignal {
  id: string
  symbol: string
  signal: 'buy' | 'sell' | 'hold'
  confidence: number
  price: number
  targetPrice: number
  stopLoss: number
  reasoning: string
  source: 'ai' | 'analyst' | 'quantum' | 'esg'
  timestamp: string
  expiry: string
  riskLevel: 'low' | 'medium' | 'high'
}

export interface RiskMetrics {
  var95: number
  var99: number
  expectedShortfall: number
  sharpeRatio: number
  sortinoRatio: number
  maxDrawdown: number
  beta: number
  correlation: number
  volatility: number
  timestamp: string
}

export interface ESGScore {
  environmental: number
  social: number
  governance: number
  overall: number
  rating: 'AAA' | 'AA' | 'A' | 'BBB' | 'BB' | 'B' | 'CCC' | 'CC' | 'C'
  timestamp: string
  factors: ESGFactors
}

export interface ESGFactors {
  carbonEmissions: number
  energyEfficiency: number
  renewableEnergy: number
  waterManagement: number
  wasteManagement: number
  laborRights: number
  communityRelations: number
  boardIndependence: number
  executiveCompensation: number
  shareholderRights: number
}

export interface ComplianceRule {
  id: string
  name: string
  description: string
  type: 'sharia' | 'esg' | 'regulatory' | 'internal'
  region: string[]
  status: 'active' | 'inactive' | 'draft'
  rules: ComplianceRuleDetail[]
  createdAt: string
  updatedAt: string
}

export interface ComplianceRuleDetail {
  field: string
  operator: 'eq' | 'ne' | 'gt' | 'lt' | 'gte' | 'lte' | 'in' | 'not_in'
  value: any
  description: string
}

export interface BlockchainTransaction {
  id: string
  hash: string
  from: string
  to: string
  value: number
  gas: number
  gasPrice: number
  nonce: number
  status: 'pending' | 'confirmed' | 'failed'
  blockNumber?: number
  timestamp: string
  type: 'p2p_trade' | 'settlement' | 'escrow' | 'reward'
  metadata: Record<string, any>
}

export interface P2PTrade {
  id: string
  sellerId: string
  buyerId: string
  energyType: 'solar' | 'wind' | 'hydro' | 'nuclear' | 'fossil'
  quantity: number
  unit: 'MWh' | 'kWh'
  price: number
  currency: string
  location: string
  deliveryDate: string
  status: 'pending' | 'confirmed' | 'delivered' | 'cancelled'
  blockchainTxId?: string
  createdAt: string
  updatedAt: string
}

export interface AIInsight {
  id: string
  type: 'market_analysis' | 'trading_recommendation' | 'risk_assessment' | 'portfolio_optimization'
  title: string
  description: string
  confidence: number
  impact: 'low' | 'medium' | 'high'
  symbols: string[]
  data: Record<string, any>
  timestamp: string
  expiry: string
  source: 'prophet' | 'rl_agent' | 'quantum' | 'esg_model'
}

export interface MarketNews {
  id: string
  title: string
  summary: string
  content: string
  source: string
  url: string
  publishedAt: string
  symbols: string[]
  sentiment: 'positive' | 'negative' | 'neutral'
  impact: 'low' | 'medium' | 'high'
  category: 'market' | 'economic' | 'political' | 'environmental' | 'social'
}

export interface Alert {
  id: string
  userId: string
  type: 'price' | 'volume' | 'news' | 'risk' | 'compliance'
  symbol?: string
  condition: string
  value: number
  status: 'active' | 'triggered' | 'acknowledged' | 'disabled'
  message: string
  createdAt: string
  triggeredAt?: string
  acknowledgedAt?: string
}

export interface ChartData {
  timestamp: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface TimeSeriesData {
  symbol: string
  interval: '1m' | '5m' | '15m' | '1h' | '4h' | '1d' | '1w' | '1M'
  data: ChartData[]
  lastUpdate: string
}

export interface WebSocketMessage {
  type: 'market_data' | 'order_update' | 'position_update' | 'trading_signal' | 'risk_alert' | 'system_status'
  data: any
  timestamp: string
  userId?: string
  sessionId?: string
}
