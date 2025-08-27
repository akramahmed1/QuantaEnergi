import React from 'react'
import { motion } from 'framer-motion'
import { 
    // CurrencyDollarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline'

const PortfolioSummary: React.FC = () => {
  const portfolio = {
    totalValue: 1250000,
    totalPnL: 45000,
    totalPnLPercent: 3.73,
    positions: [
      { symbol: 'WTI', quantity: 5000, avgPrice: 76.50, currentPrice: 78.45, pnl: 9750, pnlPercent: 2.55 },
      { symbol: 'BRENT', quantity: 3000, avgPrice: 80.20, currentPrice: 82.67, pnl: 7410, pnlPercent: 3.08 },
      { symbol: 'NATURAL_GAS', quantity: 10000, avgPrice: 3.20, currentPrice: 3.45, pnl: 2500, pnlPercent: 7.81 }
    ]
  }

  return (
    <div className="space-y-6">
      {/* Portfolio Overview */}
      <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-6">
        <h2 className="text-xl font-semibold text-secondary-900 mb-6">Portfolio Overview</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-secondary-900 mb-1">
              ${portfolio.totalValue.toLocaleString()}
            </div>
            <div className="text-sm text-secondary-600">Total Value</div>
          </div>
          
          <div className="text-center">
            <div className={`text-2xl font-bold mb-1 ${
              portfolio.totalPnL >= 0 ? 'text-success-600' : 'text-danger-600'
            }`}>
              {portfolio.totalPnL >= 0 ? '+' : ''}${portfolio.totalPnL.toLocaleString()}
            </div>
            <div className="text-sm text-secondary-600">Total P&L</div>
          </div>
          
          <div className="text-center">
            <div className={`text-2xl font-bold mb-1 ${
              portfolio.totalPnLPercent >= 0 ? 'text-success-600' : 'text-danger-600'
            }`}>
              {portfolio.totalPnLPercent >= 0 ? '+' : ''}{portfolio.totalPnLPercent.toFixed(2)}%
            </div>
            <div className="text-sm text-secondary-600">P&L %</div>
          </div>
        </div>
      </div>

      {/* Positions */}
      <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-6">
        <h3 className="text-lg font-semibold text-secondary-900 mb-4">Open Positions</h3>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-secondary-200">
            <thead className="bg-secondary-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                  Symbol
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                  Quantity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                  Avg Price
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                  Current Price
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                  P&L
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                  P&L %
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-secondary-200">
              {portfolio.positions.map((position, index) => (
                <motion.tr
                  key={position.symbol}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="hover:bg-secondary-50"
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <ChartBarIcon className="w-4 h-4 text-secondary-400 mr-2" />
                      <span className="text-sm font-medium text-secondary-900">
                        {position.symbol}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-900">
                    {position.quantity.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-900">
                    ${position.avgPrice.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-900">
                    ${position.currentPrice.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className={`flex items-center ${
                      position.pnl >= 0 ? 'text-success-600' : 'text-danger-600'
                    }`}>
                      {position.pnl >= 0 ? (
                        <TrendingUpIcon className="w-4 h-4 mr-1" />
                      ) : (
                        <TrendingDownIcon className="w-4 h-4 mr-1" />
                      )}
                      <span className="text-sm font-medium">
                        {position.pnl >= 0 ? '+' : ''}${position.pnl.toLocaleString()}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`text-sm font-medium ${
                      position.pnlPercent >= 0 ? 'text-success-600' : 'text-danger-600'
                    }`}>
                      {position.pnlPercent >= 0 ? '+' : ''}{position.pnlPercent.toFixed(2)}%
                    </span>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default PortfolioSummary
