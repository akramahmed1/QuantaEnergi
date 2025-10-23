import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ComposedChart
} from 'recharts';
import { 
  Globe, 
  AlertTriangle, 
  TrendingUp, 
  TrendingDown,
  MapPin,
  Activity,
  Shield,
  Zap,
  Droplets,
  Wind,
  Sun,
  CloudRain,
  Thermometer,
  Gauge
} from 'lucide-react';

interface GeoRiskDashboardProps {
  userId?: string;
}

const GeoRiskDashboard: React.FC<GeoRiskDashboardProps> = ({ userId = 'user123' }) => {
  const [selectedRegion, setSelectedRegion] = useState('guyana');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Sample geo-risk data
  const regions = [
    { id: 'guyana', name: 'Guyana', risk: 75, sentiment: 0.6, volatility: 0.15, color: '#8884d8' },
    { id: 'middle_east', name: 'Middle East', risk: 85, sentiment: 0.4, volatility: 0.25, color: '#ff7300' },
    { id: 'north_america', name: 'North America', risk: 35, sentiment: 0.8, volatility: 0.10, color: '#82ca9d' },
    { id: 'europe', name: 'Europe', risk: 45, sentiment: 0.7, volatility: 0.12, color: '#00c49f' },
    { id: 'asia_pacific', name: 'Asia Pacific', risk: 65, sentiment: 0.5, volatility: 0.18, color: '#ffc658' }
  ];

  const riskFactors = [
    { factor: 'Geopolitical', guyana: 30, middle_east: 90, north_america: 20, europe: 40, asia_pacific: 60 },
    { factor: 'Climate', guyana: 80, middle_east: 30, north_america: 40, europe: 50, asia_pacific: 70 },
    { factor: 'Economic', guyana: 40, middle_east: 50, north_america: 30, europe: 30, asia_pacific: 40 },
    { factor: 'Regulatory', guyana: 60, middle_east: 40, north_america: 50, europe: 60, asia_pacific: 50 },
    { factor: 'Infrastructure', guyana: 70, middle_east: 60, north_america: 30, europe: 20, asia_pacific: 50 }
  ];

  const historicalRisk = [
    { date: '2024-01-01', guyana: 70, middle_east: 80, north_america: 30, europe: 40, asia_pacific: 60 },
    { date: '2024-01-15', guyana: 75, middle_east: 85, north_america: 35, europe: 45, asia_pacific: 65 },
    { date: '2024-02-01', guyana: 80, middle_east: 90, north_america: 40, europe: 50, asia_pacific: 70 },
    { date: '2024-02-15', guyana: 75, middle_east: 85, north_america: 35, europe: 45, asia_pacific: 65 },
    { date: '2024-03-01', guyana: 70, middle_east: 80, north_america: 30, europe: 40, asia_pacific: 60 }
  ];

  const climateData = [
    { month: 'Jan', temperature: 28, rainfall: 200, humidity: 85, wind: 15 },
    { month: 'Feb', temperature: 29, rainfall: 180, humidity: 82, wind: 18 },
    { month: 'Mar', temperature: 30, rainfall: 220, humidity: 88, wind: 12 },
    { month: 'Apr', temperature: 31, rainfall: 250, humidity: 90, wind: 10 },
    { month: 'May', temperature: 32, rainfall: 300, humidity: 92, wind: 8 },
    { month: 'Jun', temperature: 33, rainfall: 350, humidity: 95, wind: 6 }
  ];

  const sentimentData = [
    { source: 'News', positive: 45, negative: 35, neutral: 20 },
    { source: 'Social Media', positive: 30, negative: 50, neutral: 20 },
    { source: 'Market Reports', positive: 60, negative: 25, neutral: 15 },
    { source: 'Analyst Views', positive: 55, negative: 30, neutral: 15 }
  ];

  const volatilityData = [
    { time: '00:00', wti: 0.02, brent: 0.03, gas: 0.05 },
    { time: '06:00', wti: 0.03, brent: 0.04, gas: 0.06 },
    { time: '12:00', wti: 0.05, brent: 0.06, gas: 0.08 },
    { time: '18:00', wti: 0.04, brent: 0.05, gas: 0.07 },
    { time: '24:00', wti: 0.02, brent: 0.03, gas: 0.05 }
  ];

  const selectedRegionData = regions.find(r => r.id === selectedRegion);

  const getRiskLevel = (risk: number) => {
    if (risk >= 80) return { level: 'CRITICAL', color: 'text-red-600', bg: 'bg-red-100' };
    if (risk >= 60) return { level: 'HIGH', color: 'text-orange-600', bg: 'bg-orange-100' };
    if (risk >= 40) return { level: 'MEDIUM', color: 'text-yellow-600', bg: 'bg-yellow-100' };
    return { level: 'LOW', color: 'text-green-600', bg: 'bg-green-100' };
  };

  const getSentimentIcon = (sentiment: number) => {
    if (sentiment >= 0.7) return <TrendingUp className="h-5 w-5 text-green-600" />;
    if (sentiment >= 0.4) return <Activity className="h-5 w-5 text-yellow-600" />;
    return <TrendingDown className="h-5 w-5 text-red-600" />;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Globe className="h-8 w-8 text-blue-600" />
              <h1 className="ml-3 text-2xl font-bold text-gray-900">Geo-Risk AI Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600">
                AI-Powered Risk Assessment
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Region Selector */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-4 py-4">
            {regions.map((region) => (
              <button
                key={region.id}
                onClick={() => setSelectedRegion(region.id)}
                className={`flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedRegion === region.id
                    ? 'bg-blue-100 text-blue-700'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                <MapPin className="h-4 w-4 mr-2" />
                {region.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* Risk Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Risk Score</p>
                  <p className="text-3xl font-bold text-gray-900">{selectedRegionData?.risk}</p>
                </div>
                <div className={`p-3 rounded-full ${getRiskLevel(selectedRegionData?.risk || 0).bg}`}>
                  <Shield className={`h-6 w-6 ${getRiskLevel(selectedRegionData?.risk || 0).color}`} />
                </div>
              </div>
              <div className="mt-4">
                <div className="flex items-center">
                  <span className={`text-sm font-medium ${getRiskLevel(selectedRegionData?.risk || 0).color}`}>
                    {getRiskLevel(selectedRegionData?.risk || 0).level}
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Sentiment</p>
                  <p className="text-3xl font-bold text-gray-900">
                    {Math.round((selectedRegionData?.sentiment || 0) * 100)}%
                  </p>
                </div>
                <div className="p-3 rounded-full bg-blue-100">
                  {getSentimentIcon(selectedRegionData?.sentiment || 0)}
                </div>
              </div>
              <div className="mt-4">
                <div className="flex items-center">
                  <span className="text-sm font-medium text-gray-600">
                    {selectedRegionData?.sentiment && selectedRegionData.sentiment >= 0.7 ? 'Positive' :
                     selectedRegionData?.sentiment && selectedRegionData.sentiment >= 0.4 ? 'Neutral' : 'Negative'}
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Volatility</p>
                  <p className="text-3xl font-bold text-gray-900">
                    {Math.round((selectedRegionData?.volatility || 0) * 100)}%
                  </p>
                </div>
                <div className="p-3 rounded-full bg-yellow-100">
                  <Zap className="h-6 w-6 text-yellow-600" />
                </div>
              </div>
              <div className="mt-4">
                <div className="flex items-center">
                  <span className="text-sm font-medium text-gray-600">
                    {selectedRegionData?.volatility && selectedRegionData.volatility >= 0.2 ? 'High' :
                     selectedRegionData?.volatility && selectedRegionData.volatility >= 0.1 ? 'Medium' : 'Low'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Risk Factors Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Factors by Region</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={riskFactors}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="factor" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="guyana" fill="#8884d8" name="Guyana" />
                <Bar dataKey="middle_east" fill="#ff7300" name="Middle East" />
                <Bar dataKey="north_america" fill="#82ca9d" name="North America" />
                <Bar dataKey="europe" fill="#00c49f" name="Europe" />
                <Bar dataKey="asia_pacific" fill="#ffc658" name="Asia Pacific" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Historical Risk Trends */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Historical Risk Trends</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={historicalRisk}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="guyana" stroke="#8884d8" strokeWidth={2} name="Guyana" />
                <Line type="monotone" dataKey="middle_east" stroke="#ff7300" strokeWidth={2} name="Middle East" />
                <Line type="monotone" dataKey="north_america" stroke="#82ca9d" strokeWidth={2} name="North America" />
                <Line type="monotone" dataKey="europe" stroke="#00c49f" strokeWidth={2} name="Europe" />
                <Line type="monotone" dataKey="asia_pacific" stroke="#ffc658" strokeWidth={2} name="Asia Pacific" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Climate and Environmental Data */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Climate Data</h3>
              <ResponsiveContainer width="100%" height={250}>
                <ComposedChart data={climateData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Legend />
                  <Bar yAxisId="left" dataKey="temperature" fill="#8884d8" name="Temperature (°C)" />
                  <Line yAxisId="right" type="monotone" dataKey="rainfall" stroke="#82ca9d" strokeWidth={2} name="Rainfall (mm)" />
                </ComposedChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Market Volatility</h3>
              <ResponsiveContainer width="100%" height={250}>
                <AreaChart data={volatilityData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Area type="monotone" dataKey="wti" stackId="1" stroke="#8884d8" fill="#8884d8" name="WTI" />
                  <Area type="monotone" dataKey="brent" stackId="1" stroke="#82ca9d" fill="#82ca9d" name="Brent" />
                  <Area type="monotone" dataKey="gas" stackId="1" stroke="#ffc658" fill="#ffc658" name="Natural Gas" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Sentiment Analysis */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Sentiment Analysis</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={sentimentData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="source" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="positive" stackId="a" fill="#82ca9d" name="Positive" />
                <Bar dataKey="neutral" stackId="a" fill="#ffc658" name="Neutral" />
                <Bar dataKey="negative" stackId="a" fill="#ff7300" name="Negative" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Recommendations */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Recommendations</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[
                { 
                  title: 'Risk Mitigation', 
                  description: 'Implement enhanced monitoring for geopolitical risks',
                  priority: 'High',
                  icon: Shield
                },
                { 
                  title: 'Climate Adaptation', 
                  description: 'Develop flood risk management strategies',
                  priority: 'Critical',
                  icon: Droplets
                },
                { 
                  title: 'Market Diversification', 
                  description: 'Consider reducing exposure to high-risk regions',
                  priority: 'Medium',
                  icon: Globe
                },
                { 
                  title: 'Infrastructure Investment', 
                  description: 'Strengthen critical infrastructure resilience',
                  priority: 'High',
                  icon: Zap
                },
                { 
                  title: 'Regulatory Compliance', 
                  description: 'Ensure adherence to regional regulations',
                  priority: 'Critical',
                  icon: AlertTriangle
                },
                { 
                  title: 'Technology Integration', 
                  description: 'Leverage AI for real-time risk monitoring',
                  priority: 'Medium',
                  icon: Activity
                }
              ].map((recommendation, index) => {
                const Icon = recommendation.icon;
                return (
                  <div key={index} className="p-4 border rounded-lg">
                    <div className="flex items-start">
                      <Icon className="h-6 w-6 text-blue-600 mt-1 mr-3" />
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900">{recommendation.title}</h4>
                        <p className="text-sm text-gray-600 mt-1">{recommendation.description}</p>
                        <div className="mt-2">
                          <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                            recommendation.priority === 'Critical' 
                              ? 'bg-red-100 text-red-800'
                              : recommendation.priority === 'High'
                              ? 'bg-orange-100 text-orange-800'
                              : 'bg-yellow-100 text-yellow-800'
                          }`}>
                            {recommendation.priority}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GeoRiskDashboard;
