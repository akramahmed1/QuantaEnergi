import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { useFormik } from 'formik';
import * as Yup from 'yup';

interface TradeData {
  id: number;
  asset: string;
  quantity: number;
  price: number;
  pnl: number;
  timestamp: string;
}

interface RiskMetrics {
  var_95: number;
  var_99: number;
  expected_shortfall: number;
  sharpe_ratio: number;
}

interface GeoRiskData {
  region: string;
  risk_level: string;
  risk_score: number;
  recommendations: string[];
}

interface QuantumOptimization {
  expected_return: number;
  risk_score: number;
  sharpe_ratio: number;
  quantum_advantage: number;
  assets: Array<{
    symbol: string;
    weight: number;
    expected_return: number;
    risk: number;
  }>;
}

interface FormValues {
  asset: string;
  quantity: number;
  price: number;
  currency: string;
}

const ProductionDashboard: React.FC = () => {
  const [trades, setTrades] = useState<TradeData[]>([]);
  const [riskMetrics, setRiskMetrics] = useState<RiskMetrics | null>(null);
  const [geoRisk, setGeoRisk] = useState<GeoRiskData | null>(null);
  const [quantumOpt, setQuantumOpt] = useState<QuantumOptimization | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Formik for trade creation
  const tradeForm = useFormik({
    initialValues: {
      asset: 'crude_oil',
      quantity: 1000,
      price: 85.50,
      currency: 'USD'
    },
    validationSchema: Yup.object({
      asset: Yup.string().required('Asset is required'),
      quantity: Yup.number().positive('Quantity must be positive').required('Quantity is required'),
      price: Yup.number().positive('Price must be positive').required('Price is required')
    }),
    onSubmit: async (values: FormValues) => {
      setLoading(true);
      try {
        const response = await fetch('/api/trades', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(values)
        });
        
        if (response.ok) {
          const result = await response.json();
          console.log('Trade created:', result);
          loadDashboardData();
        } else {
          throw new Error('Failed to create trade');
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    }
  });

  // Load dashboard data
  const loadDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');
      const authHeaders = { 'Authorization': `Bearer ${token}` };
      
      // Parallel API calls with Promise.allSettled for better error handling
      const [tradesResult, riskResult, geoRiskResult, quantumResult] = await Promise.allSettled([
        fetch('/api/trades', { headers: authHeaders }),
        fetch('/api/risk/var', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...authHeaders
          },
          body: JSON.stringify({
            prices: [85.50, 86.20, 85.80, 87.10, 86.90, 88.30, 87.50, 89.20, 88.80, 90.10]
          })
        }),
        fetch('/api/geo-risk/assess', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...authHeaders
          },
          body: JSON.stringify({
            region: 'GUYANA',
            volatility: 0.2,
            sentiment: 0.4,
            news_volume: 0.7
          })
        }),
        fetch('/api/quantum/optimize', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...authHeaders
          },
          body: JSON.stringify({
            returns: [0.15, 0.12, 0.18, 0.10, 0.08],
            risks: [0.08, 0.10, 0.12, 0.06, 0.04]
          })
        })
      ]);

      // Process trades result
      if (tradesResult.status === 'fulfilled' && tradesResult.value.ok) {
        const tradesData = await tradesResult.value.json();
        setTrades(tradesData);
      } else if (tradesResult.status === 'rejected') {
        console.warn('Trades API failed:', tradesResult.reason);
      }

      // Process risk metrics result
      if (riskResult.status === 'fulfilled' && riskResult.value.ok) {
        const riskData = await riskResult.value.json();
        setRiskMetrics({
          var_95: riskData.param_var || 0.05,
          var_99: riskData.param_var * 1.5 || 0.075,
          expected_shortfall: riskData.param_var * 1.2 || 0.06,
          sharpe_ratio: 1.4
        });
      } else if (riskResult.status === 'rejected') {
        console.warn('Risk API failed:', riskResult.reason);
      }

      // Process geo-risk result
      if (geoRiskResult.status === 'fulfilled' && geoRiskResult.value.ok) {
        const geoData = await geoRiskResult.value.json();
        setGeoRisk({
          region: geoData.risk_assessment.region,
          risk_level: geoData.risk_assessment.risk_level,
          risk_score: geoData.risk_assessment.risk_score,
          recommendations: geoData.recommendations || []
        });
      } else if (geoRiskResult.status === 'rejected') {
        console.warn('Geo-risk API failed:', geoRiskResult.reason);
      }

      // Process quantum optimization result
      if (quantumResult.status === 'fulfilled' && quantumResult.value.ok) {
        const quantumData = await quantumResult.value.json();
        setQuantumOpt(quantumData);
      } else if (quantumResult.status === 'rejected') {
        console.warn('Quantum API failed:', quantumResult.reason);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  // Generate chart data
  const priceData = [
    { date: '2024-01-01', price: 85.50, var: 0.05 },
    { date: '2024-01-02', price: 86.20, var: 0.052 },
    { date: '2024-01-03', price: 85.80, var: 0.048 },
    { date: '2024-01-04', price: 87.10, var: 0.055 },
    { date: '2024-01-05', price: 86.90, var: 0.053 },
    { date: '2024-01-06', price: 88.30, var: 0.058 },
    { date: '2024-01-07', price: 87.50, var: 0.056 },
    { date: '2024-01-08', price: 89.20, var: 0.061 },
    { date: '2024-01-09', price: 88.80, var: 0.059 },
    { date: '2024-01-10', price: 90.10, var: 0.063 }
  ];

  const portfolioData = quantumOpt?.assets || [
    { symbol: 'SOL', weight: 30, expected_return: 15, risk: 8 },
    { symbol: 'WIND', weight: 25, expected_return: 12, risk: 10 },
    { symbol: 'BAT', weight: 20, expected_return: 18, risk: 12 },
    { symbol: 'GRID', weight: 15, expected_return: 10, risk: 6 },
    { symbol: 'CARB', weight: 10, expected_return: 8, risk: 4 }
  ];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">QuantaEnergi Production Dashboard</h1>
          <p className="text-gray-600">Real-time ETRM/CTRM with AI, Quantum, and Blockchain</p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Total Trades</h3>
            <p className="text-2xl font-bold text-blue-600">{trades.length}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">VaR (95%)</h3>
            <p className="text-2xl font-bold text-red-600">
              {riskMetrics ? `${(riskMetrics.var_95 * 100).toFixed(1)}%` : 'N/A'}
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Geo-Risk</h3>
            <p className="text-2xl font-bold text-orange-600">
              {geoRisk ? geoRisk.risk_level : 'N/A'}
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Quantum Advantage</h3>
            <p className="text-2xl font-bold text-purple-600">
              {quantumOpt ? `${(quantumOpt.quantum_advantage * 100).toFixed(1)}%` : 'N/A'}
            </p>
          </div>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Price & VaR Chart */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Price & VaR Analysis</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={priceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="price" stroke="#8884d8" name="Price" />
                <Line type="monotone" dataKey="var" stroke="#82ca9d" name="VaR" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Portfolio Allocation */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Quantum Portfolio Optimization</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={portfolioData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ symbol, weight }) => `${symbol}: ${weight}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="weight"
                >
                  {portfolioData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Trade Creation Form */}
        <div className="bg-white p-6 rounded-lg shadow mb-8">
          <h3 className="text-lg font-semibold mb-4">Create New Trade</h3>
          <form onSubmit={tradeForm.handleSubmit} className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Asset</label>
              <select
                name="asset"
                value={tradeForm.values.asset}
                onChange={tradeForm.handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="crude_oil">Crude Oil</option>
                <option value="natural_gas">Natural Gas</option>
                <option value="electricity">Electricity</option>
                <option value="coal">Coal</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Quantity</label>
              <input
                type="number"
                name="quantity"
                value={tradeForm.values.quantity}
                onChange={tradeForm.handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Price</label>
              <input
                type="number"
                step="0.01"
                name="price"
                value={tradeForm.values.price}
                onChange={tradeForm.handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="flex items-end">
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Creating...' : 'Create Trade'}
              </button>
            </div>
          </form>
        </div>

        {/* Risk & Compliance */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Risk Metrics */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Risk Metrics</h3>
            {riskMetrics ? (
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">VaR (95%)</span>
                  <span className="font-semibold text-red-600">
                    {(riskMetrics.var_95 * 100).toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">VaR (99%)</span>
                  <span className="font-semibold text-red-600">
                    {(riskMetrics.var_99 * 100).toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Expected Shortfall</span>
                  <span className="font-semibold text-orange-600">
                    {(riskMetrics.expected_shortfall * 100).toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Sharpe Ratio</span>
                  <span className="font-semibold text-green-600">
                    {riskMetrics.sharpe_ratio.toFixed(2)}
                  </span>
                </div>
              </div>
            ) : (
              <p className="text-gray-500">Loading risk metrics...</p>
            )}
          </div>

          {/* Geo-Risk Assessment */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Geo-Risk Assessment</h3>
            {geoRisk ? (
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Region</span>
                  <span className="font-semibold">{geoRisk.region}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Risk Level</span>
                  <span className={`font-semibold ${
                    geoRisk.risk_level === 'HIGH' ? 'text-red-600' :
                    geoRisk.risk_level === 'MEDIUM' ? 'text-orange-600' : 'text-green-600'
                  }`}>
                    {geoRisk.risk_level}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Risk Score</span>
                  <span className="font-semibold">{(geoRisk.risk_score * 100).toFixed(1)}%</span>
                </div>
                {geoRisk.recommendations.length > 0 && (
                  <div className="mt-4">
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Recommendations:</h4>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {geoRisk.recommendations.slice(0, 2).map((rec, index) => (
                        <li key={index}>• {rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-gray-500">Loading geo-risk data...</p>
            )}
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mt-6 bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProductionDashboard;
