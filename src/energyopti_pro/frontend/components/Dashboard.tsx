/**
 * Modern dashboard component for EnergyOpti-Pro frontend.
 * 
 * This component provides a comprehensive dashboard with real-time data,
 * trading interface, risk metrics, and compliance status.
 */

import React, { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  BarElement,
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import {
  CurrencyDollarIcon,
  TrendingUpIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  UserGroupIcon,
} from '@heroicons/react/24/outline';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface DashboardProps {
  userRole: string;
  region: string;
}

interface TradingMetrics {
  totalContracts: number;
  activeTrades: number;
  dailyVolume: number;
  pnl: number;
}

interface RiskMetrics {
  var: number;
  positionLimit: number;
  correlationRisk: number;
  complianceScore: number;
}

interface MarketData {
  timestamp: string;
  power: number;
  gas: number;
  oil: number;
  carbon: number;
}

const Dashboard: React.FC<DashboardProps> = ({ userRole, region }) => {
  const [tradingMetrics, setTradingMetrics] = useState<TradingMetrics>({
    totalContracts: 0,
    activeTrades: 0,
    dailyVolume: 0,
    pnl: 0,
  });

  const [riskMetrics, setRiskMetrics] = useState<RiskMetrics>({
    var: 0,
    positionLimit: 0,
    correlationRisk: 0,
    complianceScore: 0,
  });

  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Fetch dashboard data
    fetchDashboardData();
    
    // Set up real-time updates
    const interval = setInterval(fetchDashboardData, 30000); // 30 seconds
    
    return () => clearInterval(interval);
  }, [region]);

  const fetchDashboardData = async () => {
    try {
      // Fetch trading metrics
      const tradingResponse = await fetch(`/api/v1/etrm/contracts/?region=${region}`);
      const contracts = await tradingResponse.json();
      
      // Fetch risk metrics
      const riskResponse = await fetch(`/api/v1/etrm/risk/var?region=${region}`);
      const riskData = await riskResponse.json();
      
      // Fetch market data
      const marketResponse = await fetch(`/api/v1/etrm/market/prices?region=${region}`);
      const marketPrices = await marketResponse.json();
      
      // Update state
      setTradingMetrics({
        totalContracts: contracts.length,
        activeTrades: contracts.filter((c: any) => c.status === 'active').length,
        dailyVolume: calculateDailyVolume(contracts),
        pnl: calculatePnL(contracts),
      });
      
      setRiskMetrics({
        var: riskData.var || 0,
        positionLimit: 1000000, // Mock data
        correlationRisk: 0.3, // Mock data
        complianceScore: 95, // Mock data
      });
      
      setMarketData(formatMarketData(marketPrices));
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setIsLoading(false);
    }
  };

  const calculateDailyVolume = (contracts: any[]): number => {
    return contracts.reduce((total, contract) => total + (contract.quantity || 0), 0);
  };

  const calculatePnL = (contracts: any[]): number => {
    // Mock P&L calculation
    return contracts.reduce((total, contract) => {
      const marketPrice = 75.50; // Mock market price
      const contractPrice = parseFloat(contract.price) || 0;
      return total + ((marketPrice - contractPrice) * (contract.quantity || 0));
    }, 0);
  };

  const formatMarketData = (prices: any[]): MarketData[] => {
    return prices.map(price => ({
      timestamp: new Date().toISOString(),
      power: price.commodity === 'power' ? price.price : 0,
      gas: price.commodity === 'gas' ? price.price : 0,
      oil: price.commodity === 'oil' ? price.price : 0,
      carbon: price.commodity === 'carbon' ? price.price : 0,
    }));
  };

  const chartData = {
    labels: marketData.map((_, index) => `T${index}`),
    datasets: [
      {
        label: 'Power Price (USD/MWh)',
        data: marketData.map(d => d.power),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.1,
      },
      {
        label: 'Gas Price (USD/MMBtu)',
        data: marketData.map(d => d.gas),
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.1,
      },
    ],
  };

  const riskChartData = {
    labels: ['VaR', 'Position Limit', 'Correlation Risk', 'Compliance Score'],
    datasets: [
      {
        label: 'Risk Metrics',
        data: [
          riskMetrics.var / 1000, // Convert to thousands
          riskMetrics.positionLimit / 1000000, // Convert to millions
          riskMetrics.correlationRisk * 100, // Convert to percentage
          riskMetrics.complianceScore,
        ],
        backgroundColor: [
          'rgba(239, 68, 68, 0.8)', // Red for VaR
          'rgba(59, 130, 246, 0.8)', // Blue for position limit
          'rgba(245, 158, 11, 0.8)', // Yellow for correlation
          'rgba(16, 185, 129, 0.8)', // Green for compliance
        ],
      },
    ],
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            EnergyOpti-Pro Dashboard
          </h1>
          <p className="text-gray-600 mt-2">
            Welcome back! Here's your {region} region overview.
          </p>
        </div>

        {/* Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <CurrencyDollarIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Contracts</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {tradingMetrics.totalContracts.toLocaleString()}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <TrendingUpIcon className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active Trades</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {tradingMetrics.activeTrades.toLocaleString()}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <ExclamationTriangleIcon className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Daily Volume</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {tradingMetrics.dailyVolume.toLocaleString()} MWh
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <CheckCircleIcon className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">P&L</p>
                <p className={`text-2xl font-semibold ${
                  tradingMetrics.pnl >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  ${tradingMetrics.pnl.toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Market Prices Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Market Prices
            </h3>
            <Line data={chartData} options={{
              responsive: true,
              plugins: {
                legend: {
                  position: 'top' as const,
                },
                title: {
                  display: true,
                  text: 'Real-time Market Prices',
                },
              },
              scales: {
                y: {
                  beginAtZero: true,
                },
              },
            }} />
          </div>

          {/* Risk Metrics Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Risk Metrics
            </h3>
            <Bar data={riskChartData} options={{
              responsive: true,
              plugins: {
                legend: {
                  position: 'top' as const,
                },
                title: {
                  display: true,
                  text: 'Risk Overview',
                },
              },
              scales: {
                y: {
                  beginAtZero: true,
                },
              },
            }} />
          </div>
        </div>

        {/* Quick Actions */}
        {userRole === 'trader' && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Quick Actions
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                Create Contract
              </button>
              <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors">
                Execute Trade
              </button>
              <button className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors">
                View Positions
              </button>
            </div>
          </div>
        )}

        {/* Compliance Status */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Compliance Status
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center p-4 bg-green-50 rounded-lg">
              <CheckCircleIcon className="h-5 w-5 text-green-600 mr-3" />
              <div>
                <p className="font-medium text-green-800">ADNOC Compliance</p>
                <p className="text-sm text-green-600">Status: Compliant</p>
              </div>
            </div>
            <div className="flex items-center p-4 bg-green-50 rounded-lg">
              <CheckCircleIcon className="h-5 w-5 text-green-600 mr-3" />
              <div>
                <p className="font-medium text-green-800">UAE Energy Law</p>
                <p className="text-sm text-green-600">Status: Compliant</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 