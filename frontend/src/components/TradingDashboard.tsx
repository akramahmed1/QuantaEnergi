import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  ChartBarIcon, 
  CurrencyDollarIcon, 
  TrendingUpIcon, 
  ExclamationTriangleIcon,
  CogIcon,
  BellIcon
} from '@heroicons/react/24/outline'
import { useTradingStore } from '@/store/tradingStore'
import MarketOverview from './MarketOverview'
import TradingChart from './TradingChart'
import OrderPanel from './OrderPanel'
import PortfolioSummary from './PortfolioSummary'
import TradingSignals from './TradingSignals'
import RiskMetrics from './RiskMetrics'
import ESGScore from './ESGScore'
import AIInsights from './AIInsights'
import Alerts from './Alerts'
import { websocketService } from '@/services/websocketService'

const TradingDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview')
  const [isConnected, setIsConnected] = useState(false)
  const { 
    selectedSymbol, 
    setSelectedSymbol, 
    watchlist,
    portfolio,
    getTotalPnL,
    getPortfolioValue
  } = useTradingStore()

  useEffect(() => {
    // Connect to WebSocket
    const connectWebSocket = async () => {
      try {
        await websocketService.connect('demo_user')
        setIsConnected(true)
        
        // Subscribe to watchlist symbols
        watchlist.forEach(symbol => {
          websocketService.subscribeToSymbol(symbol)
        })
      } catch (error) {
        console.error('Failed to connect to WebSocket:', error)
      }
    }

    connectWebSocket()

    return () => {
      websocketService.disconnect()
    }
  }, [watchlist])

  const tabs = [
    { id: 'overview', name: 'Overview', icon: ChartBarIcon },
    { id: 'trading', name: 'Trading', icon: TrendingUpIcon },
    { id: 'portfolio', name: 'Portfolio', icon: CurrencyDollarIcon },
    { id: 'signals', name: 'Signals', icon: ExclamationTriangleIcon },
    { id: 'risk', name: 'Risk', icon: ExclamationTriangleIcon },
    { id: 'esg', name: 'ESG', icon: ChartBarIcon },
    { id: 'ai', name: 'AI Insights', icon: CogIcon },
    { id: 'alerts', name: 'Alerts', icon: BellIcon }
  ]

  const totalPnL = getTotalPnL()
  const portfolioValue = getPortfolioValue()

  return (
    <div className="min-h-screen bg-secondary-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-secondary-200">
        <div className="max-w-9xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-secondary-900">
                EnergyOpti-Pro Trading Platform
              </h1>
              <div className="ml-4 flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-success-500' : 'bg-danger-500'}`} />
                <span className="text-sm text-secondary-600">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm text-secondary-600">Portfolio Value</p>
                <p className="text-lg font-semibold text-secondary-900">
                  ${portfolioValue.toLocaleString()}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm text-secondary-600">Total P&L</p>
                <p className={`text-lg font-semibold ${totalPnL >= 0 ? 'text-success-600' : 'text-danger-600'}`}>
                  {totalPnL >= 0 ? '+' : ''}${totalPnL.toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white border-b border-secondary-200">
        <div className="max-w-9xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:border-secondary-300'
                }`}
              >
                <tab.icon className="w-5 h-5" />
                <span>{tab.name}</span>
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-9xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <MarketOverview />
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <TradingChart />
                <TradingSignals />
              </div>
            </div>
          )}

          {activeTab === 'trading' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <TradingChart />
              </div>
              <div>
                <OrderPanel />
              </div>
            </div>
          )}

          {activeTab === 'portfolio' && (
            <PortfolioSummary />
          )}

          {activeTab === 'signals' && (
            <TradingSignals />
          )}

          {activeTab === 'risk' && (
            <RiskMetrics />
          )}

          {activeTab === 'esg' && (
            <ESGScore />
          )}

          {activeTab === 'ai' && (
            <AIInsights />
          )}

          {activeTab === 'alerts' && (
            <Alerts />
          )}
        </motion.div>
      </main>

      {/* Symbol Selector */}
      {selectedSymbol && (
        <div className="fixed bottom-4 right-4 bg-white rounded-lg shadow-lg border border-secondary-200 p-4">
          <div className="flex items-center space-x-3">
            <span className="text-sm font-medium text-secondary-900">
              {selectedSymbol}
            </span>
            <button
              onClick={() => setSelectedSymbol(null)}
              className="text-secondary-400 hover:text-secondary-600"
            >
              ×
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default TradingDashboard
