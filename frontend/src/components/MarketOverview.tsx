import React from 'react'
import { motion } from 'framer-motion'
import { 
    ArrowTrendingUpIcon,
  ArrowTrendingDownIcon, 
  CurrencyDollarIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline'

const MarketOverview: React.FC = () => {
  const marketData = [
    { symbol: 'WTI', price: 78.45, change: 2.34, changePercent: 3.07, volume: '1.2M' },
    { symbol: 'BRENT', price: 82.67, change: -1.23, changePercent: -1.47, volume: '890K' },
    { symbol: 'NATURAL_GAS', price: 3.45, change: 0.12, changePercent: 3.61, volume: '450K' },
    { symbol: 'COAL', price: 125.80, change: 5.20, changePercent: 4.31, volume: '320K' }
  ]

  return (
    <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-secondary-900">Market Overview</h2>
        <div className="flex items-center space-x-2">
          <ChartBarIcon className="w-5 h-5 text-secondary-500" />
          <span className="text-sm text-secondary-600">Live Data</span>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {marketData.map((item, index) => (
          <motion.div
            key={item.symbol}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-secondary-50 rounded-lg p-4 border border-secondary-200"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-secondary-700">{item.symbol}</span>
              <CurrencyDollarIcon className="w-4 h-4 text-secondary-500" />
            </div>
            
            <div className="text-2xl font-bold text-secondary-900 mb-1">
              ${item.price.toFixed(2)}
            </div>
            
            <div className="flex items-center justify-between">
              <div className={`flex items-center space-x-1 ${
                item.change >= 0 ? 'text-success-600' : 'text-danger-600'
              }`}>
                {item.change >= 0 ? (
                  <TrendingUpIcon className="w-4 h-4" />
                ) : (
                  <TrendingDownIcon className="w-4 h-4" />
                )}
                <span className="text-sm font-medium">
                  {item.change >= 0 ? '+' : ''}{item.change.toFixed(2)}
                </span>
              </div>
              
              <span className={`text-sm font-medium ${
                item.change >= 0 ? 'text-success-600' : 'text-danger-600'
              }`}>
                {item.change >= 0 ? '+' : ''}{item.changePercent.toFixed(2)}%
              </span>
            </div>
            
            <div className="text-xs text-secondary-500 mt-2">
              Volume: {item.volume}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

export default MarketOverview
