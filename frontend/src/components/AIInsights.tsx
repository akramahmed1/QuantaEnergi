import React from 'react'
import { motion } from 'framer-motion'
import { 
  CpuChipIcon, 
  LightBulbIcon, 
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon
} from '@heroicons/react/24/outline'

const AIInsights: React.FC = () => {
  const insights = [
    {
      id: 1,
      type: 'prediction',
      symbol: 'WTI',
      title: 'Price Breakout Expected',
      description: 'AI models predict a 15% price increase in WTI crude oil over the next 30 days based on supply constraints and geopolitical factors.',
      confidence: 87,
      impact: 'high',
      timestamp: '2 hours ago',
      recommendation: 'BUY',
      targetPrice: 90.50,
      currentPrice: 78.45
    },
    {
      id: 2,
      type: 'pattern',
      symbol: 'BRENT',
      title: 'Technical Pattern Detected',
      description: 'Machine learning algorithms have identified a bullish flag pattern with 78% historical accuracy.',
      confidence: 78,
      impact: 'medium',
      timestamp: '4 hours ago',
      recommendation: 'HOLD',
      targetPrice: 85.20,
      currentPrice: 82.67
    },
    {
      id: 3,
      type: 'sentiment',
      symbol: 'NATURAL_GAS',
      title: 'Sentiment Shift Detected',
      description: 'Social media and news sentiment analysis shows increasing positive sentiment towards natural gas futures.',
      confidence: 82,
      impact: 'medium',
      timestamp: '6 hours ago',
      recommendation: 'BUY',
      targetPrice: 3.80,
      currentPrice: 3.45
    }
  ]

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'prediction': return <ArrowTrendingUpIcon className="w-5 h-5" />
      case 'pattern': return <ChartBarIcon className="w-5 h-5" />
      case 'sentiment': return <LightBulbIcon className="w-5 h-5" />
      default: return <CpuChipIcon className="w-5 h-5" />
    }
  }

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high': return 'text-danger-600 bg-danger-100'
      case 'medium': return 'text-warning-600 bg-warning-100'
      case 'low': return 'text-success-600 bg-success-100'
      default: return 'text-secondary-600 bg-secondary-100'
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-secondary-900">AI Insights</h2>
        <div className="flex items-center space-x-2">
          <CpuChipIcon className="w-5 h-5 text-primary-500" />
          <span className="text-sm text-primary-600 font-medium">Live AI Analysis</span>
        </div>
      </div>
      
      <div className="space-y-6">
        {insights.map((insight, index) => (
          <motion.div
            key={insight.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="border border-secondary-200 rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-primary-100 rounded-lg text-primary-600">
                  {getInsightIcon(insight.type)}
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-secondary-900">
                    {insight.title}
                  </h3>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-secondary-700">
                      {insight.symbol}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getImpactColor(insight.impact)}`}>
                      {insight.impact.toUpperCase()} Impact
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="text-right">
                <div className="text-sm text-secondary-600">Confidence</div>
                <div className="text-lg font-bold text-secondary-900">
                  {insight.confidence}%
                </div>
              </div>
            </div>
            
            <p className="text-sm text-secondary-700 mb-4">
              {insight.description}
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div>
                <div className="text-sm text-secondary-600 mb-1">Recommendation</div>
                <div className={`text-lg font-bold ${
                  insight.recommendation === 'BUY' ? 'text-success-600' : 
                  insight.recommendation === 'SELL' ? 'text-danger-600' : 'text-warning-600'
                }`}>
                  {insight.recommendation}
                </div>
              </div>
              <div>
                <div className="text-sm text-secondary-600 mb-1">Target Price</div>
                <div className="text-lg font-bold text-secondary-900">
                  ${insight.targetPrice.toFixed(2)}
                </div>
              </div>
              <div>
                <div className="text-sm text-secondary-600 mb-1">Current Price</div>
                <div className="text-lg font-bold text-secondary-900">
                  ${insight.currentPrice.toFixed(2)}
                </div>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="text-xs text-secondary-500">
                Generated {insight.timestamp}
              </div>
              
              <div className="flex space-x-2">
                <button className="px-4 py-2 text-sm font-medium text-primary-600 hover:text-primary-800 transition-colors">
                  View Details
                </button>
                <button className="px-4 py-2 text-sm font-medium text-secondary-600 hover:text-secondary-800 transition-colors">
                  Dismiss
                </button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
      
      <div className="mt-6 p-4 bg-primary-50 rounded-lg border border-primary-200">
        <div className="flex items-center space-x-2 mb-2">
          <CpuChipIcon className="w-5 h-5 text-primary-500" />
          <span className="text-sm font-medium text-primary-700">AI Model Status</span>
        </div>
        <p className="text-sm text-primary-700">
          All AI models are running optimally with 99.2% uptime. 
          Real-time data processing and analysis are active across all energy commodities.
        </p>
      </div>
    </div>
  )
}

export default AIInsights
