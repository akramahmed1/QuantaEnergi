import React from 'react'
import { motion } from 'framer-motion'
import { 
  LightBulbIcon, 
  TrendingUpIcon, 
  TrendingDownIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'

const TradingSignals: React.FC = () => {
  const signals = [
    {
      id: 1,
      symbol: 'WTI',
      type: 'BUY',
      confidence: 85,
      reason: 'Strong technical breakout above resistance level',
      price: 78.45,
      target: 82.00,
      stopLoss: 76.50,
      timestamp: '2 hours ago'
    },
    {
      id: 2,
      symbol: 'BRENT',
      type: 'SELL',
      confidence: 72,
      reason: 'Bearish divergence on RSI indicator',
      price: 82.67,
      target: 79.50,
      stopLoss: 84.20,
      timestamp: '4 hours ago'
    },
    {
      id: 3,
      symbol: 'NATURAL_GAS',
      type: 'BUY',
      confidence: 91,
      reason: 'Fundamental supply constraints in Europe',
      price: 3.45,
      target: 3.80,
      stopLoss: 3.25,
      timestamp: '6 hours ago'
    }
  ]

  return (
    <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-secondary-900">AI Trading Signals</h2>
        <div className="flex items-center space-x-2">
          <LightBulbIcon className="w-5 h-5 text-primary-500" />
          <span className="text-sm text-primary-600 font-medium">Live AI</span>
        </div>
      </div>
      
      <div className="space-y-4">
        {signals.map((signal, index) => (
          <motion.div
            key={signal.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`border-l-4 rounded-r-lg p-4 ${
              signal.type === 'BUY' 
                ? 'border-success-500 bg-success-50' 
                : 'border-danger-500 bg-danger-50'
            }`}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-3">
                <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm font-medium ${
                  signal.type === 'BUY'
                    ? 'bg-success-100 text-success-700'
                    : 'bg-danger-100 text-danger-700'
                }`}>
                  {signal.type === 'BUY' ? (
                    <TrendingUpIcon className="w-4 h-4" />
                  ) : (
                    <TrendingDownIcon className="w-4 h-4" />
                  )}
                  <span>{signal.type}</span>
                </div>
                <span className="text-lg font-semibold text-secondary-900">
                  {signal.symbol}
                </span>
              </div>
              
              <div className="text-right">
                <div className="text-sm text-secondary-600">Confidence</div>
                <div className="text-lg font-bold text-secondary-900">
                  {signal.confidence}%
                </div>
              </div>
            </div>
            
            <div className="mb-3">
              <p className="text-sm text-secondary-700 mb-2">{signal.reason}</p>
              <div className="text-xs text-secondary-500">
                Generated {signal.timestamp}
              </div>
            </div>
            
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <div className="text-secondary-600 mb-1">Current Price</div>
                <div className="font-semibold text-secondary-900">
                  ${signal.price.toFixed(2)}
                </div>
              </div>
              <div>
                <div className="text-secondary-600 mb-1">Target</div>
                <div className="font-semibold text-secondary-900">
                  ${signal.target.toFixed(2)}
                </div>
              </div>
              <div>
                <div className="text-secondary-600 mb-1">Stop Loss</div>
                <div className="font-semibold text-secondary-900">
                  ${signal.stopLoss.toFixed(2)}
                </div>
              </div>
            </div>
            
            <div className="mt-4 flex space-x-2">
              <button className={`flex-1 px-3 py-2 text-sm font-medium rounded-md text-white ${
                signal.type === 'BUY'
                  ? 'bg-success-600 hover:bg-success-700'
                  : 'bg-danger-600 hover:bg-danger-700'
              } transition-colors`}>
                Execute {signal.type}
              </button>
              <button className="px-3 py-2 text-sm font-medium text-secondary-600 hover:text-secondary-800 transition-colors">
                Details
              </button>
            </div>
          </motion.div>
        ))}
      </div>
      
      <div className="mt-6 p-4 bg-secondary-50 rounded-lg border border-secondary-200">
        <div className="flex items-center space-x-2 mb-2">
          <ExclamationTriangleIcon className="w-4 h-4 text-secondary-500" />
          <span className="text-sm font-medium text-secondary-700">Risk Disclaimer</span>
        </div>
        <p className="text-xs text-secondary-600">
          AI trading signals are for informational purposes only. Past performance does not guarantee future results. 
          Always conduct your own research and consider your risk tolerance before trading.
        </p>
      </div>
    </div>
  )
}

export default TradingSignals
