import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import { motion } from 'framer-motion';
import { 
  TrendingUpIcon, 
  TrendingDownIcon, 
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';

interface TradeData {
  id: string;
  asset: string;
  quantity: number;
  price: number;
  direction: 'long' | 'short';
  status: string;
  pnl: number;
  timestamp: string;
}

interface MarketData {
  timestamp: string;
  price: number;
  volume: number;
  volatility: number;
}

interface RiskMetrics {
  var_95: number;
  var_99: number;
  expected_shortfall: number;
  portfolio_value: number;
  risk_score: number;
}

const tradeValidationSchema = Yup.object({
  asset: Yup.string().required('Asset is required'),
  quantity: Yup.number().positive('Quantity must be positive').required('Quantity is required'),
  price: Yup.number().positive('Price must be positive').required('Price is required'),
  direction: Yup.string().oneOf(['long', 'short'], 'Invalid direction').required('Direction is required'),
  currency: Yup.string().required('Currency is required')
});

const EnhancedTradingDashboard: React.FC = () => {
  const [trades, setTrades] = useState<TradeData[]>([]);
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [riskMetrics, setRiskMetrics] = useState<RiskMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Mock data for demonstration
  useEffect(() => {
    // Generate mock market data
    const mockMarketData: MarketData[] = Array.from({ length: 30 }, (_, i) => ({
      timestamp: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      price: 75 + Math.sin(i * 0.2) * 5 + Math.random() * 3,
      volume: 1000000 + Math.random() * 500000,
      volatility: 0.15 + Math.random() * 0.1
    }));
    setMarketData(mockMarketData);

    // Generate mock trades
    const mockTrades: TradeData[] = [
      {
        id: 'TRADE-001',
        asset: 'BRENT_CRUDE',
        quantity: 1000,
        price: 75.50,
        direction: 'long',
        status: 'active',
        pnl: 2750.00,
        timestamp: new Date().toISOString()
      },
      {
        id: 'TRADE-002',
        asset: 'WTI_CRUDE',
        quantity: 500,
        price: 73.25,
        direction: 'short',
        status: 'active',
        pnl: -1250.00,
        timestamp: new Date().toISOString()
      }
    ];
    setTrades(mockTrades);

    // Generate mock risk metrics
    setRiskMetrics({
      var_95: 125000,
      var_99: 185000,
      expected_shortfall: 210000,
      portfolio_value: 2500000,
      risk_score: 0.65
    });
  }, []);

  const handleTradeSubmit = async (values: any, { setSubmitting, resetForm }: any) => {
    setIsLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const newTrade: TradeData = {
        id: `TRADE-${Date.now()}`,
        asset: values.asset,
        quantity: values.quantity,
        price: values.price,
        direction: values.direction,
        status: 'pending',
        pnl: 0,
        timestamp: new Date().toISOString()
      };
      
      setTrades(prev => [newTrade, ...prev]);
      resetForm();
    } catch (error) {
      console.error('Trade submission failed:', error);
    } finally {
      setIsLoading(false);
      setSubmitting(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'pending':
        return <ClockIcon className="h-5 w-5 text-yellow-500" />;
      case 'settled':
        return <CheckCircleIcon className="h-5 w-5 text-blue-500" />;
      default:
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
    }
  };

  const getPnLColor = (pnl: number) => {
    return pnl >= 0 ? 'text-green-600' : 'text-red-600';
  };

  const pieData = [
    { name: 'Long Positions', value: trades.filter(t => t.direction === 'long').length, color: '#10B981' },
    { name: 'Short Positions', value: trades.filter(t => t.direction === 'short').length, color: '#EF4444' }
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Enhanced Trading Dashboard
          </h1>
          <p className="text-gray-600">
            Real-time ETRM/CTRM trading with advanced analytics and risk management
          </p>
        </motion.div>

        {/* Key Metrics Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        >
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <CurrencyDollarIcon className="h-8 w-8 text-green-500 mr-3" />
              <div>
                <p className="text-sm font-medium text-gray-600">Portfolio Value</p>
                <p className="text-2xl font-bold text-gray-900">
                  ${riskMetrics?.portfolio_value.toLocaleString() || '0'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <TrendingUpIcon className="h-8 w-8 text-blue-500 mr-3" />
              <div>
                <p className="text-sm font-medium text-gray-600">VaR (95%)</p>
                <p className="text-2xl font-bold text-gray-900">
                  ${riskMetrics?.var_95.toLocaleString() || '0'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <ExclamationTriangleIcon className="h-8 w-8 text-orange-500 mr-3" />
              <div>
                <p className="text-sm font-medium text-gray-600">Risk Score</p>
                <p className="text-2xl font-bold text-gray-900">
                  {(riskMetrics?.risk_score || 0) * 100}%
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <ChartBarIcon className="h-8 w-8 text-purple-500 mr-3" />
              <div>
                <p className="text-sm font-medium text-gray-600">Active Trades</p>
                <p className="text-2xl font-bold text-gray-900">
                  {trades.filter(t => t.status === 'active').length}
                </p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Charts Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8"
        >
          {/* Price Chart */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Price Movement</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={marketData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" />
                <YAxis />
                <Tooltip formatter={(value) => [`$${value}`, 'Price']} />
                <Legend />
                <Line type="monotone" dataKey="price" stroke="#3B82F6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Position Distribution */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Position Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Trading Form and Trades Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="grid grid-cols-1 lg:grid-cols-3 gap-6"
        >
          {/* Trading Form */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Create Trade</h3>
            <Formik
              initialValues={{
                asset: '',
                quantity: '',
                price: '',
                direction: 'long',
                currency: 'USD'
              }}
              validationSchema={tradeValidationSchema}
              onSubmit={handleTradeSubmit}
            >
              {({ isSubmitting }) => (
                <Form className="space-y-4">
                  <div>
                    <label htmlFor="asset" className="block text-sm font-medium text-gray-700">
                      Asset
                    </label>
                    <Field
                      as="select"
                      id="asset"
                      name="asset"
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    >
                      <option value="">Select Asset</option>
                      <option value="BRENT_CRUDE">Brent Crude</option>
                      <option value="WTI_CRUDE">WTI Crude</option>
                      <option value="NATURAL_GAS">Natural Gas</option>
                      <option value="HEATING_OIL">Heating Oil</option>
                    </Field>
                    <ErrorMessage name="asset" component="div" className="text-red-500 text-sm mt-1" />
                  </div>

                  <div>
                    <label htmlFor="quantity" className="block text-sm font-medium text-gray-700">
                      Quantity
                    </label>
                    <Field
                      type="number"
                      id="quantity"
                      name="quantity"
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      placeholder="Enter quantity"
                    />
                    <ErrorMessage name="quantity" component="div" className="text-red-500 text-sm mt-1" />
                  </div>

                  <div>
                    <label htmlFor="price" className="block text-sm font-medium text-gray-700">
                      Price
                    </label>
                    <Field
                      type="number"
                      step="0.01"
                      id="price"
                      name="price"
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      placeholder="Enter price"
                    />
                    <ErrorMessage name="price" component="div" className="text-red-500 text-sm mt-1" />
                  </div>

                  <div>
                    <label htmlFor="direction" className="block text-sm font-medium text-gray-700">
                      Direction
                    </label>
                    <Field
                      as="select"
                      id="direction"
                      name="direction"
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    >
                      <option value="long">Long</option>
                      <option value="short">Short</option>
                    </Field>
                    <ErrorMessage name="direction" component="div" className="text-red-500 text-sm mt-1" />
                  </div>

                  <div>
                    <label htmlFor="currency" className="block text-sm font-medium text-gray-700">
                      Currency
                    </label>
                    <Field
                      as="select"
                      id="currency"
                      name="currency"
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    >
                      <option value="USD">USD</option>
                      <option value="EUR">EUR</option>
                      <option value="GBP">GBP</option>
                    </Field>
                    <ErrorMessage name="currency" component="div" className="text-red-500 text-sm mt-1" />
                  </div>

                  <button
                    type="submit"
                    disabled={isSubmitting || isLoading}
                    className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoading ? 'Creating Trade...' : 'Create Trade'}
                  </button>
                </Form>
              )}
            </Formik>
          </div>

          {/* Trades Table */}
          <div className="lg:col-span-2 bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Trades</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Trade ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Asset
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Quantity
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Price
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Direction
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      P&L
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {trades.map((trade) => (
                    <motion.tr
                      key={trade.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="hover:bg-gray-50"
                    >
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {trade.id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {trade.asset}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {trade.quantity.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${trade.price.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          trade.direction === 'long' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {trade.direction.toUpperCase()}
                        </span>
                      </td>
                      <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getPnLColor(trade.pnl)}`}>
                        ${trade.pnl.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div className="flex items-center">
                          {getStatusIcon(trade.status)}
                          <span className="ml-2 capitalize">{trade.status}</span>
                        </div>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default EnhancedTradingDashboard;
