import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  ArrowUpIcon, 
  ArrowDownIcon, 
  CurrencyDollarIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline'

const OrderPanel: React.FC = () => {
  const [orderType, setOrderType] = useState<'market' | 'limit'>('market')
  const [side, setSide] = useState<'buy' | 'sell'>('buy')
  const [quantity, setQuantity] = useState('')
  const [price, setPrice] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Handle order submission
    console.log('Order submitted:', { orderType, side, quantity, price })
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-6">
      <h2 className="text-xl font-semibold text-secondary-900 mb-6">Place Order</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Order Type Selection */}
        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-2">
            Order Type
          </label>
          <div className="flex space-x-2">
            <button
              type="button"
              onClick={() => setOrderType('market')}
              className={`flex-1 px-3 py-2 text-sm font-medium rounded-md ${
                orderType === 'market'
                  ? 'bg-primary-100 text-primary-700 border border-primary-300'
                  : 'bg-secondary-100 text-secondary-700 border border-secondary-300'
              }`}
            >
              Market
            </button>
            <button
              type="button"
              onClick={() => setOrderType('limit')}
              className={`flex-1 px-3 py-2 text-sm font-medium rounded-md ${
                orderType === 'limit'
                  ? 'bg-primary-100 text-primary-700 border border-primary-300'
                  : 'bg-secondary-100 text-secondary-700 border border-secondary-300'
              }`}
            >
              Limit
            </button>
          </div>
        </div>

        {/* Buy/Sell Selection */}
        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-2">
            Side
          </label>
          <div className="flex space-x-2">
            <button
              type="button"
              onClick={() => setSide('buy')}
              className={`flex-1 px-3 py-2 text-sm font-medium rounded-md flex items-center justify-center space-x-2 ${
                side === 'buy'
                  ? 'bg-success-100 text-success-700 border border-success-300'
                  : 'bg-secondary-100 text-secondary-700 border border-secondary-300'
              }`}
            >
              <ArrowUpIcon className="w-4 h-4" />
              <span>Buy</span>
            </button>
            <button
              type="button"
              onClick={() => setSide('sell')}
              className={`flex-1 px-3 py-2 text-sm font-medium rounded-md flex items-center justify-center space-x-2 ${
                side === 'sell'
                  ? 'bg-danger-100 text-danger-700 border border-danger-300'
                  : 'bg-secondary-100 text-secondary-700 border border-secondary-300'
              }`}
            >
              <ArrowDownIcon className="w-4 h-4" />
              <span>Sell</span>
            </button>
          </div>
        </div>

        {/* Quantity Input */}
        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-2">
            Quantity (Barrels)
          </label>
          <div className="relative">
            <input
              type="number"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              className="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="1000"
              min="1"
              step="1"
            />
            <div className="absolute inset-y-0 right-0 flex items-center pr-3">
              <ChartBarIcon className="w-4 h-4 text-secondary-400" />
            </div>
          </div>
        </div>

        {/* Price Input (for limit orders) */}
        {orderType === 'limit' && (
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              Price (USD)
            </label>
            <div className="relative">
              <input
                type="number"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                className="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="78.45"
                min="0"
                step="0.01"
              />
              <div className="absolute inset-y-0 right-0 flex items-center pr-3">
                <CurrencyDollarIcon className="w-4 h-4 text-secondary-400" />
              </div>
            </div>
          </div>
        )}

        {/* Order Summary */}
        <div className="bg-secondary-50 rounded-lg p-4 border border-secondary-200">
          <h3 className="text-sm font-medium text-secondary-700 mb-2">Order Summary</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-secondary-600">Type:</span>
              <span className="font-medium text-secondary-900 capitalize">{orderType}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-secondary-600">Side:</span>
              <span className={`font-medium capitalize ${
                side === 'buy' ? 'text-success-600' : 'text-danger-600'
              }`}>
                {side}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-secondary-600">Quantity:</span>
              <span className="font-medium text-secondary-900">
                {quantity || '0'} barrels
              </span>
            </div>
            {orderType === 'limit' && (
              <div className="flex justify-between">
                <span className="text-secondary-600">Price:</span>
                <span className="font-medium text-secondary-900">
                  ${price || '0.00'}
                </span>
              </div>
            )}
            <div className="border-t border-secondary-200 pt-2">
              <div className="flex justify-between">
                <span className="text-secondary-600">Total Value:</span>
                <span className="font-medium text-secondary-900">
                  ${((parseFloat(quantity) || 0) * (parseFloat(price) || 78.45)).toFixed(2)}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          className={`w-full py-3 px-4 rounded-md font-medium text-white ${
            side === 'buy'
              ? 'bg-success-600 hover:bg-success-700 focus:ring-success-500'
              : 'bg-danger-600 hover:bg-danger-700 focus:ring-danger-500'
          } focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors`}
        >
          {side === 'buy' ? 'Buy' : 'Sell'} WTI Crude Oil
        </button>
      </form>
    </div>
  )
}

export default OrderPanel
