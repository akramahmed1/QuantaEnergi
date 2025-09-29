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
  ComposedChart
} from 'recharts';
import { 
  Database, 
  Leaf, 
  DollarSign, 
  TrendingUp,
  TrendingDown,
  Shield,
  CheckCircle,
  AlertTriangle,
  Clock,
  Zap,
  Globe,
  Activity,
  BarChart3,
  PieChart as PieChartIcon,
  Target,
  Users,
  Building,
  Award,
  Hash,
  Link,
  Eye,
  EyeOff
} from 'lucide-react';

interface CarbonNFTDashboardProps {
  userId?: string;
}

const CarbonNFTDashboard: React.FC<CarbonNFTDashboardProps> = ({ userId = 'user123' }) => {
  const [selectedTokenType, setSelectedTokenType] = useState('all');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Sample carbon NFT data
  const tokenTypes = [
    { id: 'all', name: 'All Tokens', color: '#8884d8' },
    { id: 'carbon_credit', name: 'Carbon Credit', color: '#82ca9d' },
    { id: 'renewable_energy', name: 'Renewable Energy', color: '#00c49f' },
    { id: 'carbon_offset', name: 'Carbon Offset', color: '#ffc658' },
    { id: 'esg_certificate', name: 'ESG Certificate', color: '#ff7300' }
  ];

  const portfolioData = [
    { 
      token_id: 'CNFT-1234567890ABCDEF',
      type: 'Carbon Credit',
      amount: 1000,
      value: 50000,
      status: 'Active',
      issue_date: '2024-01-15',
      expiry_date: '2025-01-15',
      blockchain_hash: '0x1234567890abcdef...',
      transaction_hash: '0xabcdef1234567890...'
    },
    { 
      token_id: 'CNFT-FEDCBA0987654321',
      type: 'Renewable Energy',
      amount: 500,
      value: 37500,
      status: 'Active',
      issue_date: '2024-01-20',
      expiry_date: '2025-01-20',
      blockchain_hash: '0xfedcba0987654321...',
      transaction_hash: '0x0987654321fedcba...'
    },
    { 
      token_id: 'CNFT-ABCDEF1234567890',
      type: 'Carbon Offset',
      amount: 2000,
      value: 100000,
      status: 'Traded',
      issue_date: '2024-01-10',
      expiry_date: '2025-01-10',
      blockchain_hash: '0xabcdef1234567890...',
      transaction_hash: '0x1234567890abcdef...'
    },
    { 
      token_id: 'CNFT-9876543210FEDCBA',
      type: 'ESG Certificate',
      amount: 150,
      value: 7500,
      status: 'Active',
      issue_date: '2024-01-25',
      expiry_date: '2025-01-25',
      blockchain_hash: '0x9876543210fedcba...',
      transaction_hash: '0xfedcba0987654321...'
    }
  ];

  const marketData = [
    { date: '2024-01-01', carbon_credit: 45, renewable_energy: 75, carbon_offset: 50, esg_certificate: 60 },
    { date: '2024-01-15', carbon_credit: 48, renewable_energy: 78, carbon_offset: 52, esg_certificate: 62 },
    { date: '2024-02-01', carbon_credit: 50, renewable_energy: 80, carbon_offset: 55, esg_certificate: 65 },
    { date: '2024-02-15', carbon_credit: 52, renewable_energy: 82, carbon_offset: 58, esg_certificate: 68 },
    { date: '2024-03-01', carbon_credit: 55, renewable_energy: 85, carbon_offset: 60, esg_certificate: 70 }
  ];

  const tradingVolume = [
    { time: '00:00', volume: 1200, transactions: 15 },
    { time: '06:00', volume: 1800, transactions: 22 },
    { time: '12:00', volume: 2500, transactions: 35 },
    { time: '18:00', volume: 2200, transactions: 28 },
    { time: '24:00', volume: 1500, transactions: 18 }
  ];

  const esgImpact = [
    { metric: 'Carbon Offset (tons)', value: 45230, change: 15.2, unit: 'tons' },
    { metric: 'Renewable Energy (MWh)', value: 12500, change: 8.5, unit: 'MWh' },
    { metric: 'ESG Score', value: 85, change: 3.2, unit: 'points' },
    { metric: 'Sustainability Index', value: 92, change: 5.1, unit: 'index' }
  ];

  const blockchainMetrics = [
    { metric: 'Total NFTs', value: 1247, change: 12.5, unit: 'tokens' },
    { metric: 'Active Tokens', value: 892, change: 8.3, unit: 'tokens' },
    { metric: 'Traded Volume', value: 2100000, change: 25.7, unit: 'USD' },
    { metric: 'Blockchain Hash Rate', value: 95.8, change: 2.1, unit: '%' }
  ];

  const tokenAllocation = [
    { name: 'Carbon Credit', value: 40, amount: 1000, color: '#82ca9d' },
    { name: 'Renewable Energy', value: 25, amount: 500, color: '#00c49f' },
    { name: 'Carbon Offset', value: 20, amount: 2000, color: '#ffc658' },
    { name: 'ESG Certificate', value: 15, amount: 150, color: '#ff7300' }
  ];

  const verificationStatus = [
    { token_id: 'CNFT-1234567890ABCDEF', verified: true, hash_valid: true, status_valid: true, expiry_valid: true },
    { token_id: 'CNFT-FEDCBA0987654321', verified: true, hash_valid: true, status_valid: true, expiry_valid: true },
    { token_id: 'CNFT-ABCDEF1234567890', verified: false, hash_valid: false, status_valid: true, expiry_valid: true },
    { token_id: 'CNFT-9876543210FEDCBA', verified: true, hash_valid: true, status_valid: true, expiry_valid: true }
  ];

  const selectedTokenTypeData = tokenTypes.find(t => t.id === selectedTokenType);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Active': return 'text-green-600 bg-green-100';
      case 'Traded': return 'text-blue-600 bg-blue-100';
      case 'Expired': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getVerificationIcon = (verified: boolean) => {
    return verified ? 
      <CheckCircle className="h-5 w-5 text-green-500" /> : 
      <AlertTriangle className="h-5 w-5 text-red-500" />;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Database className="h-8 w-8 text-green-600" />
              <h1 className="ml-3 text-2xl font-bold text-gray-900">Carbon NFT Blockchain Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600">
                Web3 Carbon Trading Platform
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Token Type Selector */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-4 py-4">
            {tokenTypes.map((type) => (
              <button
                key={type.id}
                onClick={() => setSelectedTokenType(type.id)}
                className={`flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedTokenType === type.id
                    ? 'bg-green-100 text-green-700'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                <Leaf className="h-4 w-4 mr-2" />
                {type.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {blockchainMetrics.map((metric, index) => (
              <div key={index} className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">{metric.metric}</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {metric.value > 1000 ? 
                        `$${(metric.value / 1000).toFixed(0)}K` : 
                        metric.value
                      }
                    </p>
                  </div>
                  <div className="flex items-center text-green-600">
                    <TrendingUp className="h-5 w-5" />
                    <span className="ml-1 text-sm">{metric.change}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* ESG Impact Metrics */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">ESG Impact Metrics</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {esgImpact.map((metric, index) => (
                <div key={index} className="text-center">
                  <div className="text-2xl font-bold text-gray-900">
                    {metric.value.toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-600">{metric.metric}</div>
                  <div className="flex items-center justify-center mt-2">
                    <TrendingUp className="h-4 w-4 text-green-600 mr-1" />
                    <span className="text-sm text-green-600">+{metric.change}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Market Data Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Carbon Token Price Trends</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={marketData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="carbon_credit" stroke="#82ca9d" strokeWidth={2} name="Carbon Credit" />
                <Line type="monotone" dataKey="renewable_energy" stroke="#00c49f" strokeWidth={2} name="Renewable Energy" />
                <Line type="monotone" dataKey="carbon_offset" stroke="#ffc658" strokeWidth={2} name="Carbon Offset" />
                <Line type="monotone" dataKey="esg_certificate" stroke="#ff7300" strokeWidth={2} name="ESG Certificate" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Trading Volume */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Trading Volume & Activity</h3>
            <ResponsiveContainer width="100%" height={300}>
              <ComposedChart data={tradingVolume}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Legend />
                <Bar yAxisId="left" dataKey="volume" fill="#8884d8" name="Volume (USD)" />
                <Line yAxisId="right" type="monotone" dataKey="transactions" stroke="#82ca9d" strokeWidth={2} name="Transactions" />
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          {/* Token Allocation */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Token Allocation</h3>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={tokenAllocation}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}%`}
                  >
                    {tokenAllocation.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Portfolio Summary</h3>
              <div className="space-y-4">
                {tokenAllocation.map((token, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center">
                      <div 
                        className="w-4 h-4 rounded-full mr-3" 
                        style={{ backgroundColor: token.color }}
                      ></div>
                      <div>
                        <p className="font-medium">{token.name}</p>
                        <p className="text-sm text-gray-600">{token.amount} tokens</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">{token.value}%</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Carbon NFT Portfolio */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Carbon NFT Portfolio</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Token ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Amount
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Value
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Verification
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {portfolioData.map((nft, index) => (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">
                        {nft.token_id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {nft.type}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {nft.amount} tons
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${nft.value.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(nft.status)}`}>
                          {nft.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getVerificationIcon(verificationStatus[index]?.verified || false)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Blockchain Verification */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Blockchain Verification Status</h3>
            <div className="space-y-4">
              {verificationStatus.map((status, index) => (
                <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center">
                    <Hash className="h-5 w-5 text-blue-600 mr-3" />
                    <div>
                      <p className="font-medium font-mono">{status.token_id}</p>
                      <p className="text-sm text-gray-600">Blockchain Hash Verification</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center">
                      <Shield className="h-4 w-4 text-green-600 mr-1" />
                      <span className="text-sm text-green-600">Hash Valid</span>
                    </div>
                    <div className="flex items-center">
                      <CheckCircle className="h-4 w-4 text-green-600 mr-1" />
                      <span className="text-sm text-green-600">Status Valid</span>
                    </div>
                    <div className="flex items-center">
                      <Clock className="h-4 w-4 text-green-600 mr-1" />
                      <span className="text-sm text-green-600">Not Expired</span>
                    </div>
                    {getVerificationIcon(status.verified)}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Blockchain Network Status */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Blockchain Network Status</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center">
                  <Database className="h-6 w-6 text-blue-600 mr-3" />
                  <div>
                    <p className="font-medium">Ethereum</p>
                    <p className="text-sm text-gray-600">Mainnet</p>
                  </div>
                </div>
                <CheckCircle className="h-5 w-5 text-green-500" />
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center">
                  <Link className="h-6 w-6 text-purple-600 mr-3" />
                  <div>
                    <p className="font-medium">Polygon</p>
                    <p className="text-sm text-gray-600">Layer 2</p>
                  </div>
                </div>
                <CheckCircle className="h-5 w-5 text-green-500" />
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center">
                  <Zap className="h-6 w-6 text-yellow-600 mr-3" />
                  <div>
                    <p className="font-medium">Gas Fees</p>
                    <p className="text-sm text-gray-600">Low</p>
                  </div>
                </div>
                <CheckCircle className="h-5 w-5 text-green-500" />
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center">
                  <Shield className="h-6 w-6 text-green-600 mr-3" />
                  <div>
                    <p className="font-medium">Security</p>
                    <p className="text-sm text-gray-600">High</p>
                  </div>
                </div>
                <CheckCircle className="h-5 w-5 text-green-500" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CarbonNFTDashboard;
