import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { 
  MarketData, 
  Order, 
  Position, 
  Portfolio, 
  TradingSignal, 
  RiskMetrics,
  ESGScore,
  AIInsight,
  Alert
} from '@/types/trading'

interface TradingState {
  // Market Data
  marketData: Record<string, MarketData>
  watchlist: string[]
  
  // Trading
  orders: Order[]
  positions: Position[]
  portfolio: Portfolio | null
  
  // AI & Analytics
  tradingSignals: TradingSignal[]
  riskMetrics: RiskMetrics | null
  esgScores: Record<string, ESGScore>
  aiInsights: AIInsight[]
  
  // Alerts & Notifications
  alerts: Alert[]
  
  // UI State
  selectedSymbol: string | null
  orderForm: {
    symbol: string
    side: 'buy' | 'sell'
    type: 'market' | 'limit' | 'stop' | 'stop_limit'
    quantity: number
    price?: number
    stopPrice?: number
    timeInForce: 'GTC' | 'IOC' | 'FOK' | 'DAY'
  }
  
  // Actions
  setMarketData: (symbol: string, data: MarketData) => void
  addToWatchlist: (symbol: string) => void
  removeFromWatchlist: (symbol: string) => void
  
  // Orders
  addOrder: (order: Order) => void
  updateOrder: (orderId: string, updates: Partial<Order>) => void
  cancelOrder: (orderId: string) => void
  
  // Positions
  updatePosition: (positionId: string, updates: Partial<Position>) => void
  closePosition: (positionId: string) => void
  
  // Portfolio
  updatePortfolio: (portfolio: Portfolio) => void
  
  // Trading Signals
  addTradingSignal: (signal: TradingSignal) => void
  removeTradingSignal: (signalId: string) => void
  
  // Risk & ESG
  updateRiskMetrics: (metrics: RiskMetrics) => void
  updateESGScore: (symbol: string, score: ESGScore) => void
  
  // AI Insights
  addAIInsight: (insight: AIInsight) => void
  removeAIInsight: (insightId: string) => void
  
  // Alerts
  addAlert: (alert: Alert) => void
  updateAlert: (alertId: string, updates: Partial<Alert>) => void
  removeAlert: (alertId: string) => void
  
  // UI Actions
  setSelectedSymbol: (symbol: string | null) => void
  updateOrderForm: (updates: Partial<TradingState['orderForm']>) => void
  resetOrderForm: () => void
  
  // Computed Values
  getTotalPnL: () => number
  getUnrealizedPnL: () => number
  getRealizedPnL: () => number
  getPortfolioValue: () => number
  getPositionBySymbol: (symbol: string) => Position | null
  getOrdersBySymbol: (symbol: string) => Order[]
  getActiveOrders: () => Order[]
  getFilledOrders: () => Order[]
}

const initialState = {
  marketData: {},
  watchlist: ['CRUDE_OIL', 'NATURAL_GAS', 'BRENT_OIL', 'HEATING_OIL', 'GASOLINE'],
  orders: [],
  positions: [],
  portfolio: null,
  tradingSignals: [],
  riskMetrics: null,
  esgScores: {},
  aiInsights: [],
  alerts: [],
  selectedSymbol: null,
  orderForm: {
    symbol: '',
    side: 'buy' as const,
    type: 'market' as const,
    quantity: 0,
    price: undefined,
    stopPrice: undefined,
    timeInForce: 'GTC' as const
  }
}

export const useTradingStore = create<TradingState>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,
        
        // Market Data Actions
        setMarketData: (symbol: string, data: MarketData) =>
          set((state) => ({
            marketData: { ...state.marketData, [symbol]: data }
          })),
        
        addToWatchlist: (symbol: string) =>
          set((state) => ({
            watchlist: [...state.watchlist, symbol]
          })),
        
        removeFromWatchlist: (symbol: string) =>
          set((state) => ({
            watchlist: state.watchlist.filter(s => s !== symbol)
          })),
        
        // Order Actions
        addOrder: (order: Order) =>
          set((state) => ({
            orders: [...state.orders, order]
          })),
        
        updateOrder: (orderId: string, updates: Partial<Order>) =>
          set((state) => ({
            orders: state.orders.map(order =>
              order.id === orderId ? { ...order, ...updates } : order
            )
          })),
        
        cancelOrder: (orderId: string) =>
          set((state) => ({
            orders: state.orders.map(order =>
              order.id === orderId ? { ...order, status: 'cancelled' } : order
            )
          })),
        
        // Position Actions
        updatePosition: (positionId: string, updates: Partial<Position>) =>
          set((state) => ({
            positions: state.positions.map(position =>
              position.id === positionId ? { ...position, ...updates } : position
            )
          })),
        
        closePosition: (positionId: string) =>
          set((state) => ({
            positions: state.positions.filter(position => position.id !== positionId)
          })),
        
        // Portfolio Actions
        updatePortfolio: (portfolio: Portfolio) =>
          set({ portfolio }),
        
        // Trading Signal Actions
        addTradingSignal: (signal: TradingSignal) =>
          set((state) => ({
            tradingSignals: [...state.tradingSignals, signal]
          })),
        
        removeTradingSignal: (signalId: string) =>
          set((state) => ({
            tradingSignals: state.tradingSignals.filter(signal => signal.id !== signalId)
          })),
        
        // Risk & ESG Actions
        updateRiskMetrics: (metrics: RiskMetrics) =>
          set({ riskMetrics: metrics }),
        
        updateESGScore: (symbol: string, score: ESGScore) =>
          set((state) => ({
            esgScores: { ...state.esgScores, [symbol]: score }
          })),
        
        // AI Insight Actions
        addAIInsight: (insight: AIInsight) =>
          set((state) => ({
            aiInsights: [...state.aiInsights, insight]
          })),
        
        removeAIInsight: (insightId: string) =>
          set((state) => ({
            aiInsights: state.aiInsights.filter(insight => insight.id !== insightId)
          })),
        
        // Alert Actions
        addAlert: (alert: Alert) =>
          set((state) => ({
            alerts: [...state.alerts, alert]
          })),
        
        updateAlert: (alertId: string, updates: Partial<Alert>) =>
          set((state) => ({
            alerts: state.alerts.map(alert =>
              alert.id === alertId ? { ...alert, ...updates } : alert
            )
          })),
        
        removeAlert: (alertId: string) =>
          set((state) => ({
            alerts: state.alerts.filter(alert => alert.id !== alertId)
          })),
        
        // UI Actions
        setSelectedSymbol: (symbol: string | null) =>
          set({ selectedSymbol: symbol }),
        
        updateOrderForm: (updates: Partial<TradingState['orderForm']>) =>
          set((state) => ({
            orderForm: { ...state.orderForm, ...updates }
          })),
        
        resetOrderForm: () =>
          set({ orderForm: initialState.orderForm }),
        
        // Computed Values
        getTotalPnL: () => {
          const state = get()
          return state.portfolio?.totalPnL || 0
        },
        
        getUnrealizedPnL: () => {
          const state = get()
          return state.portfolio?.unrealizedPnL || 0
        },
        
        getRealizedPnL: () => {
          const state = get()
          return state.portfolio?.realizedPnL || 0
        },
        
        getPortfolioValue: () => {
          const state = get()
          return state.portfolio?.totalValue || 0
        },
        
        getPositionBySymbol: (symbol: string) => {
          const state = get()
          return state.positions.find(position => position.symbol === symbol) || null
        },
        
        getOrdersBySymbol: (symbol: string) => {
          const state = get()
          return state.orders.filter(order => order.symbol === symbol)
        },
        
        getActiveOrders: () => {
          const state = get()
          return state.orders.filter(order => 
            ['pending', 'partial'].includes(order.status)
          )
        },
        
        getFilledOrders: () => {
          const state = get()
          return state.orders.filter(order => order.status === 'filled')
        }
      }),
      {
        name: 'trading-store',
        partialize: (state) => ({
          watchlist: state.watchlist,
          selectedSymbol: state.selectedSymbol,
          orderForm: state.orderForm
        })
      }
    ),
    {
      name: 'trading-store'
    }
  )
)
