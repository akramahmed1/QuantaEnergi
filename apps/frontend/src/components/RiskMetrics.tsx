import React from 'react'
import { motion } from 'framer-motion'
import { 
  ExclamationTriangleIcon, 
  ChartBarIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline'

const RiskMetrics: React.FC = () => {
  const riskMetrics = {
    var95: 125000,
    var99: 185000,
    maxDrawdown: 8.5,
    sharpeRatio: 1.85,
    beta: 0.92,
    correlation: 0.78
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-secondary-900">Risk Metrics</h2>
        <div className="flex items-center space-x-2">
          <ShieldCheckIcon className="w-5 h-5 text-primary-500" />
          <span className="text-sm text-primary-600 font-medium">Live Monitoring</span>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* VaR Metrics */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-secondary-900">Value at Risk</h3>
          
          <div className="bg-danger-50 border border-danger-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-danger-700">95% VaR (1-day)</span>
              <ExclamationTriangleIcon className="w-4 h-4 text-danger-500" />
            </div>
            <div className="text-2xl font-bold text-danger-700">
              ${riskMetrics.var95.toLocaleString()}
            </div>
            <div className="text-xs text-danger-600">
              Maximum expected loss with 95% confidence
            </div>
          </div>
          
          <div className="bg-warning-50 border border-warning-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-warning-700">99% VaR (1-day)</span>
              <ExclamationTriangleIcon className="w-4 h-4 text-warning-500" />
            </div>
            <div className="text-2xl font-bold text-warning-700">
              ${riskMetrics.var99.toLocaleString()}
            </div>
            <div className="text-xs text-warning-600">
              Maximum expected loss with 99% confidence
            </div>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-secondary-900">Performance</h3>
          
          <div className="bg-secondary-50 border border-secondary-200 rounded-lg p-4">
            <div className="text-sm font-medium text-secondary-700 mb-1">Max Drawdown</div>
            <div className="text-2xl font-bold text-secondary-900">
              {riskMetrics.maxDrawdown}%
            </div>
            <div className="text-xs text-secondary-600">
              Largest peak-to-trough decline
            </div>
          </div>
          
          <div className="bg-success-50 border border-success-200 rounded-lg p-4">
            <div className="text-sm font-medium text-success-700 mb-1">Sharpe Ratio</div>
            <div className="text-2xl font-bold text-success-700">
              {riskMetrics.sharpeRatio}
            </div>
            <div className="text-xs text-success-600">
              Risk-adjusted return measure
            </div>
          </div>
        </div>

        {/* Market Metrics */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-secondary-900">Market Risk</h3>
          
          <div className="bg-secondary-50 border border-secondary-200 rounded-lg p-4">
            <div className="text-sm font-medium text-secondary-700 mb-1">Beta</div>
            <div className="text-2xl font-bold text-secondary-900">
              {riskMetrics.beta}
            </div>
            <div className="text-xs text-secondary-600">
              Volatility vs. market benchmark
            </div>
          </div>
          
          <div className="bg-secondary-50 border border-secondary-200 rounded-lg p-4">
            <div className="text-sm font-medium text-secondary-700 mb-1">Correlation</div>
            <div className="text-2xl font-bold text-secondary-900">
              {riskMetrics.correlation}
            </div>
            <div className="text-xs text-secondary-600">
              Correlation with S&P 500
            </div>
          </div>
        </div>
      </div>

      {/* Risk Alerts */}
      <div className="mt-6 p-4 bg-warning-50 rounded-lg border border-warning-200">
        <div className="flex items-center space-x-2 mb-2">
          <ExclamationTriangleIcon className="w-5 h-5 text-warning-500" />
          <span className="text-sm font-medium text-warning-700">Risk Alert</span>
        </div>
        <p className="text-sm text-warning-700">
          Portfolio VaR has increased by 15% in the last 24 hours. Consider reviewing position sizes 
          and implementing additional risk controls.
        </p>
      </div>
    </div>
  )
}

export default RiskMetrics
