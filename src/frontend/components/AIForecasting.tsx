import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import axios from 'axios';

interface ForecastData {
  timestamp: string;
  actual: number;
  predicted: number;
  confidence_lower: number;
  confidence_upper: number;
}

interface ESGScore {
  environmental: number;
  social: number;
  governance: number;
  overall: number;
}

interface AIInsight {
  type: 'demand_forecast' | 'price_breakout' | 'esg_analysis' | 'risk_alert';
  title: string;
  description: string;
  confidence: number;
  impact: 'high' | 'medium' | 'low';
  timestamp: string;
}

const AIForecasting: React.FC = () => {
  const [forecastData, setForecastData] = useState<ForecastData[]>([]);
  const [esgScore, setEsgScore] = useState<ESGScore | null>(null);
  const [insights, setInsights] = useState<AIInsight[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedPeriod, setSelectedPeriod] = useState('7d');
  const [selectedMetric, setSelectedMetric] = useState('consumption');

  const generateMockForecastData = (): ForecastData[] => {
    const data: ForecastData[] = [];
    const now = new Date();
    
    for (let i = 0; i < 30; i++) {
      const date = new Date(now.getTime() + i * 24 * 60 * 60 * 1000);
      const baseValue = 1000 + Math.random() * 500;
      const predicted = baseValue + (Math.random() - 0.5) * 200;
      const confidence = 0.1;
      
      data.push({
        timestamp: date.toISOString().split('T')[0],
        actual: i < 7 ? baseValue : 0,
        predicted: predicted,
        confidence_lower: predicted * (1 - confidence),
        confidence_upper: predicted * (1 + confidence),
      });
    }
    
    return data;
  };

  const generateMockESGScore = (): ESGScore => ({
    environmental: 85 + Math.random() * 15,
    social: 80 + Math.random() * 20,
    governance: 90 + Math.random() * 10,
    overall: 85 + Math.random() * 15,
  });

  const generateMockInsights = (): AIInsight[] => [
    {
      type: 'demand_forecast',
      title: 'Peak Demand Expected',
      description: 'AI predicts 15% increase in energy demand over next 7 days due to weather patterns',
      confidence: 0.89,
      impact: 'high',
      timestamp: new Date().toISOString(),
    },
    {
      type: 'price_breakout',
      title: 'Price Volatility Alert',
      description: 'Detected unusual price movement patterns suggesting potential breakout',
      confidence: 0.76,
      impact: 'medium',
      timestamp: new Date().toISOString(),
    },
    {
      type: 'esg_analysis',
      title: 'ESG Score Improvement',
      description: 'Portfolio ESG score improved by 8% due to recent renewable energy investments',
      confidence: 0.92,
      impact: 'low',
      timestamp: new Date().toISOString(),
    },
  ];

  useEffect(() => {
    // Load mock data initially
    setForecastData(generateMockForecastData());
    setEsgScore(generateMockESGScore());
    setInsights(generateMockInsights());
  }, []);

  const handleForecastRequest = async () => {
    setLoading(true);
    try {
      // In production, this would call the actual backend API
      // const response = await axios.post('/api/disruptive/forecasting/forecast', {
      //   period: selectedPeriod,
      //   metric: selectedMetric,
      // });
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Update with new mock data
      setForecastData(generateMockForecastData());
      setEsgScore(generateMockESGScore());
      setInsights(generateMockInsights());
      
      toast.success('AI forecast updated successfully!');
    } catch (error) {
      toast.error('Failed to update forecast');
      console.error('Forecast error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'demand_forecast': return '📈';
      case 'price_breakout': return '⚡';
      case 'esg_analysis': return '🌱';
      case 'risk_alert': return '⚠️';
      default: return '💡';
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high': return 'text-red-600 bg-red-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h2 className="text-2xl font-bold text-gray-900">AI-Powered Forecasting</h2>
          <p className="text-gray-600">Advanced ML predictions for energy demand and market trends</p>
        </div>
        <button
          onClick={handleForecastRequest}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center space-x-2"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Updating...</span>
            </>
          ) : (
            <>
              <span>🔄</span>
              <span>Update Forecast</span>
            </>
          )}
        </button>
      </motion.div>

      {/* Controls */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white p-4 rounded-lg shadow-sm border"
      >
        <div className="flex space-x-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Forecast Period</label>
            <select
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="7d">7 Days</option>
              <option value="14d">14 Days</option>
              <option value="30d">30 Days</option>
              <option value="90d">90 Days</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Metric</label>
            <select
              value={selectedMetric}
              onChange={(e) => setSelectedMetric(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="consumption">Energy Consumption</option>
              <option value="price">Energy Price</option>
              <option value="demand">Grid Demand</option>
              <option value="renewable">Renewable Output</option>
            </select>
          </div>
        </div>
      </motion.div>

      {/* Forecast Chart */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white p-6 rounded-lg shadow-sm border"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Demand Forecast</h3>
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={forecastData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Area
              type="monotone"
              dataKey="actual"
              stackId="1"
              stroke="#8884d8"
              fill="#8884d8"
              fillOpacity={0.6}
              name="Actual"
            />
            <Area
              type="monotone"
              dataKey="predicted"
              stackId="2"
              stroke="#82ca9d"
              fill="#82ca9d"
              fillOpacity={0.6}
              name="Predicted"
            />
            <Area
              type="monotone"
              dataKey="confidence_upper"
              stackId="3"
              stroke="#ffc658"
              fill="#ffc658"
              fillOpacity={0.3}
              name="Confidence Upper"
            />
            <Area
              type="monotone"
              dataKey="confidence_lower"
              stackId="4"
              stroke="#ffc658"
              fill="#ffc658"
              fillOpacity={0.3}
              name="Confidence Lower"
            />
          </AreaChart>
        </ResponsiveContainer>
      </motion.div>

      {/* ESG Score */}
      {esgScore && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white p-6 rounded-lg shadow-sm border"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">ESG Score Analysis</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{esgScore.environmental.toFixed(0)}</div>
              <div className="text-sm text-gray-600">Environmental</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{esgScore.social.toFixed(0)}</div>
              <div className="text-sm text-gray-600">Social</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{esgScore.governance.toFixed(0)}</div>
              <div className="text-sm text-gray-600">Governance</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-indigo-600">{esgScore.overall.toFixed(0)}</div>
              <div className="text-sm text-gray-600">Overall</div>
            </div>
          </div>
        </motion.div>
      )}

      {/* AI Insights */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-white p-6 rounded-lg shadow-sm border"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Insights</h3>
        <div className="space-y-3">
          {insights.map((insight, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 + index * 0.1 }}
              className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg"
            >
              <span className="text-2xl">{getInsightIcon(insight.type)}</span>
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-1">
                  <h4 className="font-medium text-gray-900">{insight.title}</h4>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getImpactColor(insight.impact)}`}>
                    {insight.impact}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-2">{insight.description}</p>
                <div className="flex items-center space-x-4 text-xs text-gray-500">
                  <span>Confidence: {(insight.confidence * 100).toFixed(0)}%</span>
                  <span>{new Date(insight.timestamp).toLocaleString()}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
};

export default AIForecasting;
