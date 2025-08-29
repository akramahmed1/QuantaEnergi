import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { 
  ChartBarIcon, 
  CurrencyDollarIcon, 
  ArrowTrendingUpIcon, 
  ExclamationTriangleIcon,
  CogIcon,
  BellIcon,
  CpuChipIcon,
  CubeIcon,
  WifiIcon,
  ShieldCheckIcon
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
import AIForecasting from './AIForecasting'
import QuantumOptimization from './QuantumOptimization'
import BlockchainSmartContracts from './BlockchainSmartContracts'
import IoTIntegration from './IoTIntegration'
import ComplianceMultiRegion from './ComplianceMultiRegion'
import { websocketService } from '@/services/websocketService'

const TradingDashboard: React.FC = () => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('overview')
  const [isConnected, setIsConnected] = useState(false)
  const { 
    selectedSymbol, 
    setSelectedSymbol, 
    portfolio,
    getTotalPnL,
    getPortfolioValue
  } = useTradingStore()

  // Handle URL parameters for tab navigation
  useEffect(() => {
    const tabParam = searchParams.get('tab')
    if (tabParam && tabs.some(tab => tab.id === tabParam)) {
      setActiveTab(tabParam)
    }
  }, [searchParams])

  // Update URL when tab changes
  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId)
    navigate(`/dashboard?tab=${tabId}`, { replace: true })
  }

  useEffect(() => {
    // Connect to WebSocket
    const connectWebSocket = async () => {
      try {
        await websocketService.connect('demo_user')
        setIsConnected(true)
        
        // Subscribe to portfolio symbols
        if (portfolio.positions && portfolio.positions.length > 0) {
          portfolio.positions.forEach((item) => {
            if (item.symbol) {
              websocketService.subscribeToSymbol(item.symbol)
            }
          })
        }
      } catch (error) {
        console.error('Failed to connect to WebSocket:', error)
      }
    }

    connectWebSocket()

    return () => {
      websocketService.disconnect()
    }
  }, [portfolio.positions])

  const tabs = [
    { id: 'overview', name: 'Overview', icon: ChartBarIcon, description: 'Market overview and trading signals' },
    { id: 'trading', name: 'Trading', icon: ArrowTrendingUpIcon, description: 'Active trading and order management' },
    { id: 'portfolio', name: 'Portfolio', icon: CurrencyDollarIcon, description: 'Portfolio analysis and performance' },
    { id: 'ai-forecasting', name: 'AI Forecasting', icon: CpuChipIcon, description: 'ML-powered demand and price predictions' },
    { id: 'quantum', name: 'Quantum Optimization', icon: CubeIcon, description: 'Quantum portfolio optimization' },
    { id: 'blockchain', name: 'Blockchain', icon: ShieldCheckIcon, description: 'Smart contracts and carbon credits' },
    { id: 'iot', name: 'IoT Integration', icon: WifiIcon, description: 'Real-time infrastructure monitoring' },
    { id: 'compliance', name: 'Compliance', icon: ShieldCheckIcon, description: 'Multi-region regulatory compliance' },
    { id: 'signals', name: 'Signals', icon: ExclamationTriangleIcon, description: 'Trading signals and alerts' },
    { id: 'risk', name: 'Risk', icon: ExclamationTriangleIcon, description: 'Risk metrics and analysis' },
    { id: 'esg', name: 'ESG', icon: ChartBarIcon, description: 'Environmental, Social, Governance scoring' },
    { id: 'ai-insights', name: 'AI Insights', icon: CogIcon, description: 'Advanced AI analytics' },
    { id: 'alerts', name: 'Alerts', icon: BellIcon, description: 'System alerts and notifications' }
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
                EnergyOpti-Pro: Disruptive Energy Trading SaaS
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
          <div className="flex space-x-1 overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => handleTabChange(tab.id)}
                className={`flex flex-col items-center space-y-1 py-3 px-3 border-b-2 font-medium text-xs min-w-max ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:border-secondary-300'
                }`}
                title={tab.description}
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
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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

          {activeTab === 'ai-forecasting' && (
            <AIForecasting />
          )}

          {activeTab === 'quantum' && (
            <QuantumOptimization />
          )}

          {activeTab === 'blockchain' && (
            <BlockchainSmartContracts />
          )}

          {activeTab === 'iot' && (
            <IoTIntegration />
          )}

          {activeTab === 'compliance' && (
            <ComplianceMultiRegion />
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

          {activeTab === 'ai-insights' && (
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
