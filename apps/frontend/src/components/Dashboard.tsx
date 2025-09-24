import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

const Dashboard: React.FC = () => {
  const navigate = useNavigate()

  const { data: trades, isLoading, error } = useQuery({
    queryKey: ['trades'],
    queryFn: async () => {
      const token = localStorage.getItem('token')
      const response = await axios.get('http://localhost:8000/api/v1/trades', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      return response.data
    }
  })

  const handleLogout = () => {
    localStorage.removeItem('token')
    navigate('/login')
  }

  if (isLoading) return <div className="p-4">Loading...</div>
  if (error) return <div className="p-4 text-red-500">Error loading trades</div>

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">QuantaEnergi Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/trade')}
                className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700"
              >
                New Trade
              </button>
              <button
                onClick={() => navigate('/analytics')}
                className="bg-purple-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-purple-700"
              >
                Analytics
              </button>
              <button
                onClick={() => navigate('/compliance')}
                className="bg-green-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-green-700"
              >
                Compliance
              </button>
              <button
                onClick={handleLogout}
                className="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="border-4 border-dashed border-gray-200 rounded-lg h-96 p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Recent Trades</h2>
            
            {trades && trades.length > 0 ? (
              <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
                <table className="min-w-full divide-y divide-gray-300">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Trade ID
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Commodity
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Quantity
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Price
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {trades.map((trade: any) => (
                      <tr key={trade.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {trade.trade_id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {trade.commodity}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {trade.quantity}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          ${trade.price}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                            {trade.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-12">
                <p className="text-gray-500">No trades found. Create your first trade!</p>
                <button
                  onClick={() => navigate('/trade')}
                  className="mt-4 bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700"
                >
                  Create Trade
                </button>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

export default Dashboard
