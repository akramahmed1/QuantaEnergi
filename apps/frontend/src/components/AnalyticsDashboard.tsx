import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import axios from 'axios';

interface ForecastData {
  ds: string;
  yhat: number;
  yhat_lower: number;
  yhat_upper: number;
}

interface ForecastResponse {
  commodity: string;
  forecast_period: number;
  created_at: string;
  forecast_data: ForecastData[];
  model_accuracy: number;
  trend?: number[];
  seasonal?: number[];
}

interface MarketInsights {
  commodity: string;
  current_price: number;
  price_change_30d: number;
  volatility: number;
  market_sentiment: string;
  recommendation: string;
  risk_level: string;
  generated_at: string;
}

interface PortfolioOptimization {
  optimization_type: string;
  selected_assets: string[];
  allocation: Record<string, number>;
  expected_return: number;
  risk_score: number;
  sharpe_ratio: number;
  budget_used: number;
  optimization_time: string;
  quantum_advantage: boolean;
}

const AnalyticsDashboard: React.FC = () => {
  const [selectedCommodity, setSelectedCommodity] = useState('crude_oil');
  const [forecastDays, setForecastDays] = useState(30);

  // Fetch forecast data
  const { data: forecast, isLoading: forecastLoading, refetch: refetchForecast } = useQuery({
    queryKey: ['forecast', selectedCommodity, forecastDays],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await axios.post('http://localhost:8000/api/v1/forecast', {
        commodity: selectedCommodity,
        days_ahead: forecastDays,
        include_components: true
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data as ForecastResponse;
    },
    enabled: false
  });

  // Fetch market insights
  const { data: insights, isLoading: insightsLoading } = useQuery({
    queryKey: ['insights', selectedCommodity],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await axios.get(`http://localhost:8000/api/v1/forecast/insights/${selectedCommodity}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data as MarketInsights;
    }
  });

  // Fetch portfolio optimization
  const { data: portfolio, isLoading: portfolioLoading } = useQuery({
    queryKey: ['portfolio'],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await axios.post('http://localhost:8000/api/v1/optimize/portfolio', {
        assets: ['crude_oil', 'natural_gas', 'electricity', 'coal'],
        expected_returns: [0.05, 0.03, 0.02, 0.04],
        risk_matrix: [
          [0.01, 0.005, 0.002, 0.003],
          [0.005, 0.02, 0.001, 0.002],
          [0.002, 0.001, 0.03, 0.001],
          [0.003, 0.002, 0.001, 0.025]
        ],
        risk_tolerance: 0.5,
        budget: 1000000
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data as PortfolioOptimization;
    }
  });

  // Create forecast mutation
  const createForecastMutation = useMutation({
    mutationFn: async () => {
      await refetchForecast();
    }
  });

  // Prepare chart data
  const forecastChartData = forecast?.forecast_data.map(item => ({
    date: new Date(item.ds).toLocaleDateString(),
    forecast: item.yhat,
    lower: item.yhat_lower,
    upper: item.yhat_upper
  })) || [];

  const portfolioData = portfolio ? Object.entries(portfolio.allocation).map(([asset, allocation]) => ({
    asset,
    allocation: allocation * 100
  })) : [];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'bullish': return 'text-green-600';
      case 'bearish': return 'text-red-600';
      case 'volatile': return 'text-yellow-600';
      default: return 'text-gray-600';
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'text-green-600';
      case 'medium': return 'text-yellow-600';
      case 'high': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Analytics Dashboard</h1>
          <p className="text-gray-600">AI-powered forecasting, quantum optimization, and blockchain analytics</p>
        </div>

        {/* Controls */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Commodity</label>
              <select
                value={selectedCommodity}
                onChange={(e) => setSelectedCommodity(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="crude_oil">Crude Oil</option>
                <option value="natural_gas">Natural Gas</option>
                <option value="electricity">Electricity</option>
                <option value="coal">Coal</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Forecast Days</label>
              <select
                value={forecastDays}
                onChange={(e) => setForecastDays(Number(e.target.value))}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value={7}>7 Days</option>
                <option value={30}>30 Days</option>
                <option value={90}>90 Days</option>
              </select>
            </div>
            <div className="flex items-end">
              <button
                onClick={() => createForecastMutation.mutate()}
                disabled={createForecastMutation.isPending}
                className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 disabled:opacity-50"
              >
                {createForecastMutation.isPending ? 'Generating...' : 'Generate Forecast'}
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Market Insights */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Market Insights</h2>
            {insightsLoading ? (
              <div className="animate-pulse">Loading insights...</div>
            ) : insights ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Current Price</p>
                    <p className="text-2xl font-bold">${insights.current_price.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">30d Change</p>
                    <p className={`text-2xl font-bold ${insights.price_change_30d >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {insights.price_change_30d >= 0 ? '+' : ''}{insights.price_change_30d.toFixed(2)}%
                    </p>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Volatility</p>
                    <p className="text-lg font-semibold">{insights.volatility.toFixed(2)}%</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Sentiment</p>
                    <p className={`text-lg font-semibold ${getSentimentColor(insights.market_sentiment)}`}>
                      {insights.market_sentiment.toUpperCase()}
                    </p>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Risk Level</p>
                  <p className={`text-lg font-semibold ${getRiskColor(insights.risk_level)}`}>
                    {insights.risk_level.toUpperCase()}
                  </p>
                </div>
                <div className="bg-gray-50 p-3 rounded-md">
                  <p className="text-sm text-gray-600">Recommendation</p>
                  <p className="text-sm">{insights.recommendation}</p>
                </div>
              </div>
            ) : (
              <div className="text-gray-500">No insights available</div>
            )}
          </div>

          {/* Portfolio Optimization */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Portfolio Optimization</h2>
            {portfolioLoading ? (
              <div className="animate-pulse">Loading portfolio...</div>
            ) : portfolio ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Expected Return</p>
                    <p className="text-2xl font-bold text-green-600">{(portfolio.expected_return * 100).toFixed(2)}%</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Risk Score</p>
                    <p className="text-2xl font-bold text-red-600">{portfolio.risk_score.toFixed(3)}</p>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Sharpe Ratio</p>
                    <p className="text-lg font-semibold">{portfolio.sharpe_ratio.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Optimization Type</p>
                    <p className="text-lg font-semibold">{portfolio.optimization_type}</p>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Selected Assets</p>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {portfolio.selected_assets.map((asset, index) => (
                      <span key={index} className="bg-indigo-100 text-indigo-800 px-2 py-1 rounded text-sm">
                        {asset}
                      </span>
                    ))}
                  </div>
                </div>
                {portfolio.quantum_advantage && (
                  <div className="bg-purple-50 border border-purple-200 rounded-md p-3">
                    <p className="text-sm text-purple-800 font-medium">🚀 Quantum Advantage Active</p>
                    <p className="text-xs text-purple-600">Using quantum algorithms for optimization</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-gray-500">No portfolio data available</div>
            )}
          </div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Price Forecast Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Price Forecast</h2>
            {forecastLoading ? (
              <div className="animate-pulse h-64 bg-gray-200 rounded"></div>
            ) : forecastChartData.length > 0 ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={forecastChartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line 
                      type="monotone" 
                      dataKey="forecast" 
                      stroke="#8884d8" 
                      strokeWidth={2}
                      name="Forecast"
                    />
                    <Line 
                      type="monotone" 
                      dataKey="lower" 
                      stroke="#82ca9d" 
                      strokeDasharray="5 5"
                      name="Lower Bound"
                    />
                    <Line 
                      type="monotone" 
                      dataKey="upper" 
                      stroke="#ffc658" 
                      strokeDasharray="5 5"
                      name="Upper Bound"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-500">
                Click "Generate Forecast" to see predictions
              </div>
            )}
            {forecast && (
              <div className="mt-4 text-sm text-gray-600">
                Model Accuracy: {(forecast.model_accuracy * 100).toFixed(1)}%
              </div>
            )}
          </div>

          {/* Portfolio Allocation Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Portfolio Allocation</h2>
            {portfolioLoading ? (
              <div className="animate-pulse h-64 bg-gray-200 rounded"></div>
            ) : portfolioData.length > 0 ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={portfolioData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ asset, allocation }) => `${asset}: ${allocation.toFixed(1)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="allocation"
                    >
                      {portfolioData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-500">
                No portfolio data available
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
