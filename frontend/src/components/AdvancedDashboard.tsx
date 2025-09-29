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
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts';
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Activity, 
  Shield, 
  Zap,
  Globe,
  Brain,
  Database,
  BarChart3,
  PieChart as PieChartIcon,
  Target,
  AlertTriangle,
  CheckCircle,
  Clock,
  Users,
  Building,
  Leaf,
  Atom
} from 'lucide-react';

interface AdvancedDashboardProps {
  userId?: string;
}

const AdvancedDashboard: React.FC<AdvancedDashboardProps> = ({ userId = 'user123' }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Sample data for charts
  const portfolioData = [
    { name: 'Jan', value: 1200000, pnl: 45000, risk: 2.1 },
    { name: 'Feb', value: 1250000, pnl: 50000, risk: 1.8 },
    { name: 'Mar', value: 1300000, pnl: 50000, risk: 2.3 },
    { name: 'Apr', value: 1280000, pnl: -20000, risk: 2.8 },
    { name: 'May', value: 1350000, pnl: 70000, risk: 2.0 },
    { name: 'Jun', value: 1400000, pnl: 50000, risk: 1.9 }
  ];

  const marketData = [
    { time: '09:00', wti: 78.45, brent: 82.67, gas: 3.45 },
    { time: '10:00', wti: 78.60, brent: 82.80, gas: 3.48 },
    { time: '11:00', wti: 78.30, brent: 82.50, gas: 3.42 },
    { time: '12:00', wti: 78.80, brent: 83.10, gas: 3.50 },
    { time: '13:00', wti: 79.10, brent: 83.40, gas: 3.52 },
    { time: '14:00', wti: 78.90, brent: 83.20, gas: 3.49 }
  ];

  const riskMetrics = [
    { metric: 'VaR 95%', value: 125000, change: -5.2, status: 'good' },
    { metric: 'VaR 99%', value: 185000, change: 2.1, status: 'warning' },
    { metric: 'Max Drawdown', value: 8.5, change: -1.2, status: 'good' },
    { metric: 'Sharpe Ratio', value: 1.85, change: 0.3, status: 'excellent' }
  ];

  const assetAllocation = [
    { name: 'Crude Oil', value: 40, color: '#8884d8' },
    { name: 'Natural Gas', value: 25, color: '#82ca9d' },
    { name: 'Refined Products', value: 20, color: '#ffc658' },
    { name: 'Renewables', value: 15, color: '#00c49f' }
  ];

  const esgData = [
    { subject: 'Environmental', A: 85, B: 90, fullMark: 100 },
    { subject: 'Social', A: 78, B: 85, fullMark: 100 },
    { subject: 'Governance', A: 82, B: 88, fullMark: 100 },
    { subject: 'Transparency', A: 88, B: 92, fullMark: 100 },
    { subject: 'Innovation', A: 75, B: 80, fullMark: 100 }
  ];

  const quantumOptimization = [
    { method: 'Quantum QAOA', sharpe: 1.92, time: 0.8, advantage: true },
    { method: 'Classical PuLP', sharpe: 1.85, time: 2.1, advantage: false },
    { method: 'NumPy Fallback', sharpe: 1.78, time: 0.3, advantage: false }
  ];

  const geoRiskData = [
    { region: 'Guyana', risk: 75, sentiment: 0.6, volatility: 0.15 },
    { region: 'Middle East', risk: 85, sentiment: 0.4, volatility: 0.25 },
    { region: 'North America', risk: 35, sentiment: 0.8, volatility: 0.10 },
    { region: 'Europe', risk: 45, sentiment: 0.7, volatility: 0.12 },
    { region: 'Asia Pacific', risk: 65, sentiment: 0.5, volatility: 0.18 }
  ];

  const complianceStatus = [
    { framework: 'REMIT', status: 'Compliant', violations: 0, score: 95 },
    { framework: 'FERC', status: 'Compliant', violations: 0, score: 92 },
    { framework: 'CFTC', status: 'Warning', violations: 2, score: 85 },
    { framework: 'Islamic Finance', status: 'Compliant', violations: 0, score: 98 }
  ];

  const tabs = [
    { id: 'overview', name: 'Overview', icon: BarChart3 },
    { id: 'trading', name: 'Trading', icon: TrendingUp },
    { id: 'risk', name: 'Risk Analytics', icon: Shield },
    { id: 'quantum', name: 'Quantum', icon: Atom },
    { id: 'blockchain', name: 'Blockchain', icon: Database },
    { id: 'compliance', name: 'Compliance', icon: CheckCircle },
    { id: 'esg', name: 'ESG', icon: Leaf }
  ];

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {riskMetrics.map((metric, index) => (
          <div key={index} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{metric.metric}</p>
                <p className="text-2xl font-bold text-gray-900">
                  {typeof metric.value === 'number' && metric.value > 1000 
                    ? `$${(metric.value / 1000).toFixed(0)}K`
                    : metric.value
                  }
                </p>
              </div>
              <div className={`flex items-center ${
                metric.status === 'excellent' ? 'text-green-600' :
                metric.status === 'good' ? 'text-blue-600' :
                metric.status === 'warning' ? 'text-yellow-600' : 'text-red-600'
              }`}>
                {metric.change > 0 ? <TrendingUp className="h-5 w-5" /> : <TrendingDown className="h-5 w-5" />}
                <span className="ml-1 text-sm">{Math.abs(metric.change)}%</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Portfolio Performance Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Portfolio Performance</h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={portfolioData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip formatter={(value, name) => [
              name === 'value' ? `$${(value as number).toLocaleString()}` : value,
              name === 'value' ? 'Portfolio Value' : name
            ]} />
            <Legend />
            <Area type="monotone" dataKey="value" stroke="#8884d8" fill="#8884d8" fillOpacity={0.3} />
            <Area type="monotone" dataKey="pnl" stroke="#82ca9d" fill="#82ca9d" fillOpacity={0.3} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Asset Allocation */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Asset Allocation</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={assetAllocation}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}%`}
              >
                {assetAllocation.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Market Data</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={marketData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="wti" stroke="#8884d8" strokeWidth={2} />
              <Line type="monotone" dataKey="brent" stroke="#82ca9d" strokeWidth={2} />
              <Line type="monotone" dataKey="gas" stroke="#ffc658" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );

  const renderQuantum = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quantum Optimization Comparison</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={quantumOptimization}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="method" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="sharpe" fill="#8884d8" name="Sharpe Ratio" />
            <Bar dataKey="time" fill="#82ca9d" name="Time (s)" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quantum Advantage</h3>
          <div className="space-y-4">
            {quantumOptimization.map((method, index) => (
              <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <p className="font-medium">{method.method}</p>
                  <p className="text-sm text-gray-600">Sharpe: {method.sharpe}</p>
                </div>
                <div className={`px-3 py-1 rounded-full text-sm ${
                  method.advantage 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {method.advantage ? 'Quantum Advantage' : 'Classical'}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Optimization Status</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Qiskit Available</span>
              <CheckCircle className="h-5 w-5 text-green-500" />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">PuLP Available</span>
              <CheckCircle className="h-5 w-5 text-green-500" />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Quantum Hardware</span>
              <Clock className="h-5 w-5 text-yellow-500" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderBlockchain = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <Database className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Carbon NFTs</p>
              <p className="text-2xl font-bold text-gray-900">1,247</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <Leaf className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Carbon Offset (tons)</p>
              <p className="text-2xl font-bold text-gray-900">45,230</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <DollarSign className="h-8 w-8 text-yellow-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Value</p>
              <p className="text-2xl font-bold text-gray-900">$2.1M</p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Carbon NFT Portfolio</h3>
        <div className="space-y-4">
          {[
            { type: 'Carbon Credit', amount: 1000, value: 50000, status: 'Active' },
            { type: 'Renewable Energy', amount: 500, value: 37500, status: 'Active' },
            { type: 'Carbon Offset', amount: 2000, value: 100000, status: 'Traded' },
            { type: 'ESG Certificate', amount: 150, value: 7500, status: 'Active' }
          ].map((nft, index) => (
            <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <p className="font-medium">{nft.type}</p>
                <p className="text-sm text-gray-600">{nft.amount} tons</p>
              </div>
              <div className="text-right">
                <p className="font-medium">${nft.value.toLocaleString()}</p>
                <p className={`text-sm ${
                  nft.status === 'Active' ? 'text-green-600' : 'text-blue-600'
                }`}>{nft.status}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderCompliance = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {complianceStatus.map((framework, index) => (
          <div key={index} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">{framework.framework}</h3>
              <div className={`px-3 py-1 rounded-full text-sm ${
                framework.status === 'Compliant' 
                  ? 'bg-green-100 text-green-800'
                  : framework.status === 'Warning'
                  ? 'bg-yellow-100 text-yellow-800'
                  : 'bg-red-100 text-red-800'
              }`}>
                {framework.status}
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Score</span>
                <span className="font-medium">{framework.score}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Violations</span>
                <span className="font-medium">{framework.violations}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Compliance Timeline</h3>
        <div className="space-y-4">
          {[
            { date: '2024-01-15', event: 'REMIT Report Submitted', status: 'Completed' },
            { date: '2024-01-20', event: 'FERC Audit', status: 'Completed' },
            { date: '2024-01-25', event: 'CFTC Review', status: 'In Progress' },
            { date: '2024-02-01', event: 'Islamic Finance Assessment', status: 'Scheduled' }
          ].map((event, index) => (
            <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <p className="font-medium">{event.event}</p>
                <p className="text-sm text-gray-600">{event.date}</p>
              </div>
              <div className={`px-3 py-1 rounded-full text-sm ${
                event.status === 'Completed' 
                  ? 'bg-green-100 text-green-800'
                  : event.status === 'In Progress'
                  ? 'bg-yellow-100 text-yellow-800'
                  : 'bg-blue-100 text-blue-800'
              }`}>
                {event.status}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderESG = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">ESG Performance</h3>
        <ResponsiveContainer width="100%" height={300}>
          <RadarChart data={esgData}>
            <PolarGrid />
            <PolarAngleAxis dataKey="subject" />
            <PolarRadiusAxis angle={30} domain={[0, 100]} />
            <Radar name="Current" dataKey="A" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
            <Radar name="Target" dataKey="B" stroke="#82ca9d" fill="#82ca9d" fillOpacity={0.6} />
            <Legend />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Environmental Impact</h3>
          <div className="space-y-4">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Carbon Footprint</span>
              <span className="font-medium">-15.2%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Renewable Energy</span>
              <span className="font-medium">78%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Waste Reduction</span>
              <span className="font-medium">23%</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Social Impact</h3>
          <div className="space-y-4">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Community Investment</span>
              <span className="font-medium">$2.1M</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Employee Satisfaction</span>
              <span className="font-medium">92%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Diversity Index</span>
              <span className="font-medium">85%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return renderOverview();
      case 'quantum':
        return renderQuantum();
      case 'blockchain':
        return renderBlockchain();
      case 'compliance':
        return renderCompliance();
      case 'esg':
        return renderESG();
      default:
        return renderOverview();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Zap className="h-8 w-8 text-blue-600" />
              <h1 className="ml-3 text-2xl font-bold text-gray-900">QuantaEnergi Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600">
                Welcome back, <span className="font-medium">Trader</span>
              </div>
              <div className="h-8 w-8 bg-blue-600 rounded-full flex items-center justify-center">
                <Users className="h-5 w-5 text-white" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center px-1 py-4 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-5 w-5 mr-2" />
                  {tab.name}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <AlertTriangle className="h-5 w-5 text-red-400" />
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <p className="mt-1 text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        ) : (
          renderContent()
        )}
      </div>
    </div>
  );
};

export default AdvancedDashboard;
