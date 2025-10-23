import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

export interface MarketData {
  symbol: string
  price: number
  change: number
  changePercent: number
  volume: string
  timestamp: string
}

export interface Order {
  id: string
  symbol: string
  type: 'market' | 'limit'
  side: 'buy' | 'sell'
  quantity: number
  price: number
  status: 'pending' | 'filled' | 'cancelled'
  timestamp: string
}

export interface Position {
  symbol: string
  quantity: number
  avgPrice: number
  currentPrice: number
  pnl: number
  pnlPercent: number
}

export interface Portfolio {
  totalValue: number
  totalPnL: number
  totalPnLPercent: number
  positions: Position[]
}

export interface TradingSignal {
  id: string
  symbol: string
  type: 'BUY' | 'SELL' | 'HOLD'
  confidence: number
  reason: string
  price: number
  target: number
  stopLoss: number
  timestamp: string
}

export interface RiskMetrics {
  var95: number
  var99: number
  maxDrawdown: number
  sharpeRatio: number
  beta: number
  correlation: number
}

export interface ESGScore {
  overall: number
  environmental: number
  social: number
  governance: number
}

export interface AIInsight {
  id: string
  type: string
  symbol: string
  title: string
  description: string
  confidence: number
  impact: string
  recommendation: string
  targetPrice: number
  currentPrice: number
  timestamp: string
}

export interface Alert {
  id: string
  type: 'warning' | 'info' | 'success' | 'error'
  title: string
  message: string
  timestamp: string
  read: boolean
}

interface TradingState {
  // Market Data
  marketData: MarketData[]
  selectedSymbol: string | null
  
  // Trading
  orders: Order[]
  positions: Position[]
  portfolio: Portfolio
  
  // AI & Analytics
  tradingSignals: TradingSignal[]
  riskMetrics: RiskMetrics
  esgScore: ESGScore
  aiInsights: AIInsight[]
  
  // UI State
  alerts: Alert[]
  activeTab: string
  
  // Actions
  setSelectedSymbol: (symbol: string | null) => void
  addOrder: (order: Order) => void
  updateOrder: (id: string, updates: Partial<Order>) => void
  addPosition: (position: Position) => void
  updatePosition: (symbol: string, updates: Partial<Position>) => void
  addAlert: (alert: Alert) => void
  markAlertAsRead: (id: string) => void
  dismissAlert: (id: string) => void
  setActiveTab: (tab: string) => void
  
  // Computed Values
  getTotalPnL: () => number
  getPortfolioValue: () => number
  getWatchlist: () => string[]
}

export const useTradingStore = create<TradingState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial State
        marketData: [
          {
            symbol: 'WTI',
            price: 78.45,
            change: 2.34,
            changePercent: 3.07,
            volume: '1.2M',
            timestamp: new Date().toISOString()
          },
          {
            symbol: 'BRENT',
            price: 82.67,
            change: -1.23,
            changePercent: -1.47,
            volume: '890K',
            timestamp: new Date().toISOString()
          },
          {
            symbol: 'NATURAL_GAS',
            price: 3.45,
            change: 0.12,
            changePercent: 3.61,
            volume: '450K',
            timestamp: new Date().toISOString()
          }
        ],
        selectedSymbol: null,
        orders: [],
        positions: [
          {
            symbol: 'WTI',
            quantity: 5000,
            avgPrice: 76.50,
            currentPrice: 78.45,
            pnl: 9750,
            pnlPercent: 2.55
          },
          {
            symbol: 'BRENT',
            quantity: 3000,
            avgPrice: 80.20,
            currentPrice: 82.67,
            pnl: 7410,
            pnlPercent: 3.08
          }
        ],
        portfolio: {
          totalValue: 1250000,
          totalPnL: 45000,
          totalPnLPercent: 3.73,
          positions: []
        },
        tradingSignals: [],
        riskMetrics: {
          var95: 125000,
          var99: 185000,
          maxDrawdown: 8.5,
          sharpeRatio: 1.85,
          beta: 0.92,
          correlation: 0.78
        },
        esgScore: {
          overall: 78,
          environmental: 82,
          social: 75,
          governance: 79
        },
        aiInsights: [],
        alerts: [],
        activeTab: 'overview',

        // Actions
        setSelectedSymbol: (symbol) => set({ selectedSymbol: symbol }),
        
        addOrder: (order) => set((state) => ({
          orders: [...state.orders, order]
        })),
        
        updateOrder: (id, updates) => set((state) => ({
          orders: state.orders.map(order =>
            order.id === id ? { ...order, ...updates } : order
          )
        })),
        
        addPosition: (position) => set((state) => ({
          positions: [...state.positions, position]
        })),
        
        updatePosition: (symbol, updates) => set((state) => ({
          positions: state.positions.map(position =>
            position.symbol === symbol ? { ...position, ...updates } : position
          )
        })),
        
        addAlert: (alert) => set((state) => ({
          alerts: [alert, ...state.alerts]
        })),
        
        markAlertAsRead: (id) => set((state) => ({
          alerts: state.alerts.map(alert =>
            alert.id === id ? { ...alert, read: true } : alert
          )
        })),
        
        dismissAlert: (id) => set((state) => ({
          alerts: state.alerts.filter(alert => alert.id !== id)
        })),
        
        setActiveTab: (tab) => set({ activeTab: tab }),

        // Computed Values
        getTotalPnL: () => {
          const state = get()
          return state.positions.reduce((total, position) => total + position.pnl, 0)
        },
        
        getPortfolioValue: () => {
          const state = get()
          return state.portfolio.totalValue
        },
        
        getWatchlist: () => {
          const state = get()
          return state.marketData.map(data => data.symbol)
        }
      }),
      {
        name: 'trading-store',
        partialize: (state) => ({
          selectedSymbol: state.selectedSymbol,
          activeTab: state.activeTab
        })
      }
    ),
    {
      name: 'trading-store'
    }
  )
)
