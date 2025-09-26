import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { toast } from 'react-hot-toast';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

// Types
interface VaRMetrics {
  var_95: number;
  var_99: number;
  expected_shortfall_95: number;
  expected_shortfall_99: number;
  portfolio_risk_score: number;
}

interface PortfolioSummary {
  total_value: number;
  num_positions: number;
  position_breakdown: Array<{
    commodity: string;
    value: number;
    percentage: number;
  }>;
}

interface RiskData {
  portfolio_id: string;
  confidence_level: number;
  var_metrics: VaRMetrics;
  portfolio_summary: PortfolioSummary;
  calculated_at: string;
  method: string;
  ml_insights?: {
    ml_available: boolean;
    predicted_risk?: number;
    confidence?: number;
  };
  stress_test?: {
    stress_test_results: {
      [key: string]: {
        scenario: string;
        stress_factor: number;
        original_value: number;
        stressed_value: number;
        loss_amount: number;
        loss_percentage: number;
      };
    };
    overall_stress_score: number;
  };
}

// API functions
const fetchRiskData = async (portfolioId: string, includeStressTest: boolean = false): Promise<RiskData> => {
  const params = new URLSearchParams({
    portfolio_id: portfolioId,
    include_stress_test: includeStressTest.toString()
  });
  
  const response = await fetch(`/api/v1/risk/var?${params}`);
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Risk data fetch failed: ${response.status}`);
  }
  
  return response.json();
};

const fetchStressTestData = async (portfolioId: string, scenarios: string[]): Promise<any> => {
  const params = new URLSearchParams({
    portfolio_id: portfolioId,
    scenarios: scenarios.join(',')
  });
  
  const response = await fetch(`/api/v1/risk/stress-test?${params}`);
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Stress test failed: ${response.status}`);
  }
  
  return response.json();
};

const RiskDashboard: React.FC = () => {
  const [portfolioId, setPortfolioId] = useState('test_portfolio_001');
  const [includeStressTest, setIncludeStressTest] = useState(false);
  const [selectedTimeframe, setSelectedTimeframe] = useState('1D');

  // Fetch risk data
  const { data: riskData, isLoading: riskLoading, error: riskError } = useQuery({
    queryKey: ['risk-data', portfolioId, includeStressTest],
    queryFn: () => fetchRiskData(portfolioId, includeStressTest),
    refetchInterval: 30000, // Refetch every 30 seconds
    retry: 3
  });

  // Fetch stress test data
  const { data: stressTestData, isLoading: stressTestLoading } = useQuery({
    queryKey: ['stress-test', portfolioId],
    queryFn: () => fetchStressTestData(portfolioId, ['market_crash', 'oil_price_shock', 'interest_rate_spike']),
    enabled: includeStressTest,
    retry: 2
  });

  // Handle errors
  useEffect(() => {
    if (riskError) {
      toast.error(`Risk data error: ${riskError.message}`);
    }
  }, [riskError]);

  // Chart configurations
  const varChartData = {
    labels: ['95% VaR', '99% VaR', 'ES 95%', 'ES 99%'],
    datasets: [
      {
        label: 'Risk Metrics ($)',
        data: riskData ? [
          riskData.var_metrics.var_95,
          riskData.var_metrics.var_99,
          riskData.var_metrics.expected_shortfall_95,
          riskData.var_metrics.expected_shortfall_99
        ] : [],
        backgroundColor: [
          'rgba(255, 99, 132, 0.8)',
          'rgba(255, 159, 64, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(75, 192, 192, 0.8)'
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(255, 159, 64, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(75, 192, 192, 1)'
        ],
        borderWidth: 2
      }
    ]
  };

  const portfolioAllocationData = {
    labels: riskData?.portfolio_summary.position_breakdown.map(pos => pos.commodity.replace('_', ' ').toUpperCase()) || [],
    datasets: [
      {
        data: riskData?.portfolio_summary.position_breakdown.map(pos => pos.value) || [],
        backgroundColor: [
          '#FF6384',
          '#36A2EB',
          '#FFCE56',
          '#4BC0C0',
          '#9966FF',
          '#FF9F40'
        ],
        borderWidth: 2,
        borderColor: '#fff'
      }
    ]
  };

  const stressTestData_chart = stressTestData ? {
    labels: Object.keys(stressTestData.stress_test_results.stress_test_results || {}),
    datasets: [
      {
        label: 'Loss Percentage (%)',
        data: Object.values(stressTestData.stress_test_results.stress_test_results || {}).map((result: any) => result.loss_percentage),
        backgroundColor: 'rgba(255, 99, 132, 0.8)',
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 2
      }
    ]
  } : null;

  // Mock P&L data for demonstration
  const pnlData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'P&L ($)',
        data: [120000, -45000, 180000, -23000, 95000, 67000, 110000],
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.4,
        fill: true
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Risk Metrics Overview'
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value: any) {
            return '$' + value.toLocaleString();
          }
        }
      }
    }
  };

  const pnlChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Portfolio P&L Trend'
      }
    },
    scales: {
      y: {
        beginAtZero: false,
        ticks: {
          callback: function(value: any) {
            return '$' + value.toLocaleString();
          }
        }
      }
    }
  };

  const stressTestOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Stress Test Results'
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value: any) {
            return value + '%';
          }
        }
      }
    }
  };

  if (riskLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading risk data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Risk Dashboard</h1>
          <p className="mt-2 text-gray-600">Portfolio risk analysis and VaR calculations</p>
        </div>

        {/* Controls */}
        <div className="bg-white shadow rounded-lg p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Portfolio ID
              </label>
              <input
                type="text"
                value={portfolioId}
                onChange={(e) => setPortfolioId(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter portfolio ID"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Timeframe
              </label>
              <select
                value={selectedTimeframe}
                onChange={(e) => setSelectedTimeframe(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="1D">1 Day</option>
                <option value="1W">1 Week</option>
                <option value="1M">1 Month</option>
                <option value="3M">3 Months</option>
              </select>
            </div>
            <div className="flex items-center">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={includeStressTest}
                  onChange={(e) => setIncludeStressTest(e.target.checked)}
                  className="mr-2"
                />
                <span className="text-sm text-gray-700">Include Stress Test</span>
              </label>
            </div>
            <div className="flex items-end">
              <button
                onClick={() => window.location.reload()}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Refresh Data
              </button>
            </div>
          </div>
        </div>

        {/* Risk Metrics Cards */}
        {riskData && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
                    <span className="text-red-600 font-bold">VaR</span>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">95% VaR</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    ${riskData.var_metrics.var_95.toLocaleString()}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center">
                    <span className="text-orange-600 font-bold">ES</span>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Expected Shortfall</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    ${riskData.var_metrics.expected_shortfall_95.toLocaleString()}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-blue-600 font-bold">RS</span>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Risk Score</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {(riskData.var_metrics.portfolio_risk_score * 100).toFixed(1)}%
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                    <span className="text-green-600 font-bold">TV</span>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Total Value</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    ${riskData.portfolio_summary.total_value.toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* VaR Metrics Chart */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Risk Metrics</h3>
            <div className="h-64">
              <Bar data={varChartData} options={chartOptions} />
            </div>
          </div>

          {/* Portfolio Allocation */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Portfolio Allocation</h3>
            <div className="h-64">
              <Doughnut data={portfolioAllocationData} options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'bottom' as const,
                  }
                }
              }} />
            </div>
          </div>
        </div>

        {/* P&L Trend and Stress Test */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* P&L Trend */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">P&L Trend</h3>
            <div className="h-64">
              <Line data={pnlData} options={pnlChartOptions} />
            </div>
          </div>

          {/* Stress Test Results */}
          {includeStressTest && stressTestData && (
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Stress Test Results</h3>
              <div className="h-64">
                {stressTestData_chart && (
                  <Bar data={stressTestData_chart} options={stressTestOptions} />
                )}
              </div>
            </div>
          )}
        </div>

        {/* ML Insights */}
        {riskData?.ml_insights?.ml_available && (
          <div className="bg-white shadow rounded-lg p-6 mb-8">
            <h3 className="text-lg font-medium text-gray-900 mb-4">ML Insights</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <p className="text-sm text-gray-500">Predicted Risk</p>
                <p className="text-2xl font-semibold text-blue-600">
                  {(riskData.ml_insights.predicted_risk * 100).toFixed(1)}%
                </p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-500">Confidence</p>
                <p className="text-2xl font-semibold text-green-600">
                  {(riskData.ml_insights.confidence * 100).toFixed(1)}%
                </p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-500">Model Version</p>
                <p className="text-lg font-semibold text-gray-600">v1.0</p>
              </div>
            </div>
          </div>
        )}

        {/* Portfolio Details */}
        {riskData && (
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Portfolio Details</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Commodity
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Value
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Percentage
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Risk Level
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {riskData.portfolio_summary.position_breakdown.map((position, index) => (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {position.commodity.replace('_', ' ').toUpperCase()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${position.value.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {position.percentage}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          position.percentage > 30 ? 'bg-red-100 text-red-800' :
                          position.percentage > 20 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {position.percentage > 30 ? 'High' : position.percentage > 20 ? 'Medium' : 'Low'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="mt-8 text-center text-gray-500 text-sm">
          <p>Last updated: {riskData?.calculated_at ? new Date(riskData.calculated_at).toLocaleString() : 'Never'}</p>
          <p>Method: {riskData?.method || 'numpy.percentile'}</p>
        </div>
      </div>
    </div>
  );
};

export default RiskDashboard;
