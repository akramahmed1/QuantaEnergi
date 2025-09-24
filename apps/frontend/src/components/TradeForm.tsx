import React, { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

interface TradeData {
  trade_type: string
  commodity: string
  quantity: number
  price: number
  currency: string
  counterparty_id: string
  counterparty_name: string
  delivery_date: string
  delivery_location: string
  trade_direction: string
  is_islamic_compliant: boolean
}

const TradeForm: React.FC = () => {
  const [formData, setFormData] = useState<TradeData>({
    trade_type: 'spot',
    commodity: 'crude_oil',
    quantity: 0,
    price: 0,
    currency: 'USD',
    counterparty_id: '',
    counterparty_name: '',
    delivery_date: '',
    delivery_location: '',
    trade_direction: 'buy',
    is_islamic_compliant: false
  })
  
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const tradeMutation = useMutation({
    mutationFn: async (data: TradeData) => {
      const token = localStorage.getItem('token')
      const response = await axios.post('http://localhost:8000/api/v1/capture', data, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trades'] })
      navigate('/dashboard')
    },
    onError: (error) => {
      console.error('Trade creation failed:', error)
    }
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    tradeMutation.mutate(formData)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : 
              type === 'number' ? parseFloat(value) || 0 : value
    })
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md mx-auto">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Create New Trade</h2>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700">Trade Type</label>
              <select
                name="trade_type"
                value={formData.trade_type}
                onChange={handleChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              >
                <option value="spot">Spot</option>
                <option value="forward">Forward</option>
                <option value="futures">Futures</option>
                <option value="options">Options</option>
                <option value="swap">Swap</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Commodity</label>
              <select
                name="commodity"
                value={formData.commodity}
                onChange={handleChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              >
                <option value="crude_oil">Crude Oil</option>
                <option value="natural_gas">Natural Gas</option>
                <option value="electricity">Electricity</option>
                <option value="coal">Coal</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Quantity</label>
                <input
                  type="number"
                  name="quantity"
                  value={formData.quantity}
                  onChange={handleChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Price</label>
                <input
                  type="number"
                  name="price"
                  value={formData.price}
                  onChange={handleChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Counterparty ID</label>
              <input
                type="text"
                name="counterparty_id"
                value={formData.counterparty_id}
                onChange={handleChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Counterparty Name</label>
              <input
                type="text"
                name="counterparty_name"
                value={formData.counterparty_name}
                onChange={handleChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Delivery Date</label>
              <input
                type="date"
                name="delivery_date"
                value={formData.delivery_date}
                onChange={handleChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Delivery Location</label>
              <input
                type="text"
                name="delivery_location"
                value={formData.delivery_location}
                onChange={handleChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Trade Direction</label>
              <select
                name="trade_direction"
                value={formData.trade_direction}
                onChange={handleChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              >
                <option value="buy">Buy</option>
                <option value="sell">Sell</option>
              </select>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                name="is_islamic_compliant"
                checked={formData.is_islamic_compliant}
                onChange={handleChange}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
              <label className="ml-2 block text-sm text-gray-900">
                Islamic Compliant
              </label>
            </div>

            <div>
              <button
                type="submit"
                disabled={tradeMutation.isPending}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
              >
                {tradeMutation.isPending ? 'Creating Trade...' : 'Create Trade'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

export default TradeForm
