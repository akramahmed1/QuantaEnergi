import React from 'react'
import { motion } from 'framer-motion'
import { ChartBarIcon, CalendarIcon } from '@heroicons/react/24/outline'

const TradingChart: React.FC = () => {
  const chartData = [
    { time: '09:00', price: 78.20 },
    { time: '10:00', price: 78.45 },
    { time: '11:00', price: 78.80 },
    { time: '12:00', price: 79.10 },
    { time: '13:00', price: 78.90 },
    { time: '14:00', price: 78.45 },
    { time: '15:00', price: 78.20 },
    { time: '16:00', price: 78.45 }
  ]

  const maxPrice = Math.max(...chartData.map(d => d.price))
  const minPrice = Math.min(...chartData.map(d => d.price))
  const range = maxPrice - minPrice

  return (
    <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-secondary-900">WTI Crude Oil</h2>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <CalendarIcon className="w-4 h-4 text-secondary-500" />
            <span className="text-sm text-secondary-600">1H</span>
          </div>
          <div className="flex items-center space-x-2">
            <ChartBarIcon className="w-4 h-4 text-secondary-500" />
            <span className="text-sm text-secondary-600">Candlestick</span>
          </div>
        </div>
      </div>

      <div className="mb-4">
        <div className="text-3xl font-bold text-secondary-900 mb-1">
          ${chartData[chartData.length - 1].price.toFixed(2)}
        </div>
        <div className="text-sm text-secondary-600">
          Last updated: {new Date().toLocaleTimeString()}
        </div>
      </div>

      <div className="relative h-64 mb-4">
        <svg className="w-full h-full" viewBox="0 0 400 200">
          {/* Grid lines */}
          {[0, 1, 2, 3, 4].map(i => (
            <line
              key={i}
              x1="0"
              y1={i * 50}
              x2="400"
              y2={i * 50}
              stroke="#e5e7eb"
              strokeWidth="1"
            />
          ))}
          
          {/* Price line */}
          <polyline
            fill="none"
            stroke="#3b82f6"
            strokeWidth="2"
            points={chartData.map((d, i) => 
              `${(i / (chartData.length - 1)) * 400},${200 - ((d.price - minPrice) / range) * 200}`
            ).join(' ')}
          />
          
          {/* Data points */}
          {chartData.map((d, i) => (
            <circle
              key={i}
              cx={(i / (chartData.length - 1)) * 400}
              cy={200 - ((d.price - minPrice) / range) * 200}
              r="3"
              fill="#3b82f6"
            />
          ))}
        </svg>
      </div>

      <div className="flex justify-between text-xs text-secondary-500">
        <span>${minPrice.toFixed(2)}</span>
        <span>${maxPrice.toFixed(2)}</span>
      </div>

      <div className="mt-4 grid grid-cols-4 gap-4 text-center">
        <div>
          <div className="text-sm text-secondary-600">Open</div>
          <div className="font-semibold text-secondary-900">${chartData[0].price.toFixed(2)}</div>
        </div>
        <div>
          <div className="text-sm text-secondary-600">High</div>
          <div className="font-semibold text-secondary-900">${maxPrice.toFixed(2)}</div>
        </div>
        <div>
          <div className="text-sm text-secondary-600">Low</div>
          <div className="font-semibold text-secondary-900">${minPrice.toFixed(2)}</div>
        </div>
        <div>
          <div className="text-sm text-secondary-600">Volume</div>
          <div className="font-semibold text-secondary-900">1.2M</div>
        </div>
      </div>
    </div>
  )
}

export default TradingChart
