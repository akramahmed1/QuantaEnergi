import React, { useState, useEffect } from 'react';
import {
  setCreditLimit,
  getCreditLimit,
  getAllCreditLimits,
  calculateExposure,
  getExposure,
  checkCreditAvailability,
  getCreditAvailability,
  generateCreditReport,
  getCreditDashboard,
  CreditLimit,
  CreditExposure,
  formatCurrency,
  formatPercentage
} from '../services/tradingApi';

interface CreditManagementDashboardProps {
  userId?: string;
}

const CreditManagementDashboard: React.FC<CreditManagementDashboardProps> = ({ userId = 'user123' }) => {
  // State management
  const [creditLimits, setCreditLimits] = useState<CreditLimit[]>([]);
  const [exposures, setExposures] = useState<CreditExposure[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'limits' | 'exposure' | 'reports'>('overview');
  const [dashboardData, setDashboardData] = useState<any>(null);

  // New credit limit form state
  const [newCreditLimit, setNewCreditLimit] = useState<CreditLimit>({
    counterparty_id: 'CP001',
    limit_amount: 1000000,
    currency: 'USD',
    risk_rating: 'A',
    expiry_date: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    terms: {}
  });

  // Exposure calculation state
  const [exposureCalculation, setExposureCalculation] = useState({
    counterparty_id: 'CP001',
    positions: [
      { commodity: 'crude_oil', notional_value: 500000, mark_to_market: 520000 },
      { commodity: 'natural_gas', notional_value: 300000, mark_to_market: 310000 }
    ]
  });

  // Load initial data
  useEffect(() => {
    loadCreditLimits();
    loadCreditDashboard();
  }, []);

  const loadCreditLimits = async () => {
    try {
      setLoading(true);
      const result = await getAllCreditLimits();
      if (result.success) {
        setCreditLimits(result.data);
      }
    } catch (err) {
      setError('Failed to load credit limits');
      console.error('Error loading credit limits:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadCreditDashboard = async () => {
    try {
      const result = await getCreditDashboard();
      if (result.success) {
        setDashboardData(result.data);
      }
    } catch (err) {
      console.error('Error loading credit dashboard:', err);
    }
  };

  const handleSetCreditLimit = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await setCreditLimit(newCreditLimit);
      
      if (result.success) {
        alert('Credit limit set successfully!');
        await loadCreditLimits(); // Refresh the list
        await loadCreditDashboard(); // Refresh dashboard
        
        // Reset form
        setNewCreditLimit({
          counterparty_id: 'CP001',
          limit_amount: 1000000,
          currency: 'USD',
          risk_rating: 'A',
          expiry_date: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          terms: {}
        });
      }
    } catch (err) {
      setError('Failed to set credit limit');
      console.error('Error setting credit limit:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCalculateExposure = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await calculateExposure(exposureCalculation.counterparty_id, exposureCalculation.positions);
      
      if (result.success) {
        // Add to exposures list
        setExposures(prev => [result.data, ...prev]);
        alert('Exposure calculated successfully!');
      }
    } catch (err) {
      setError('Failed to calculate exposure');
      console.error('Error calculating exposure:', err);
    } finally {
      setLoading(false);
    }
    }
  };

  const handleCheckCreditAvailability = async (counterpartyId: string, tradeAmount: number) => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await checkCreditAvailability(counterpartyId, tradeAmount);
      
      if (result.success) {
        const message = result.data.available 
          ? `Credit available! Remaining: ${formatCurrency(result.data.remaining_credit)}`
          : `Credit insufficient! Required: ${formatCurrency(tradeAmount)}`;
        alert(message);
      }
    } catch (err) {
      setError('Failed to check credit availability');
      console.error('Error checking credit availability:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateCreditReport = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await generateCreditReport();
      
      if (result.success) {
        alert(`Credit report generated! Total counterparties: ${result.data.total_counterparties}, Total exposure: ${formatCurrency(result.data.total_exposure)}`);
        await loadCreditDashboard(); // Refresh dashboard
      }
    } catch (err) {
      setError('Failed to generate credit report');
      console.error('Error generating credit report:', err);
    } finally {
      setLoading(false);
    }
  };

  const getRiskRatingColor = (rating: string) => {
    const colors: Record<string, string> = {
      'A': 'bg-green-100 text-green-800',
      'B': 'bg-blue-100 text-blue-800',
      'C': 'bg-yellow-100 text-yellow-800',
      'D': 'bg-orange-100 text-orange-800',
      'E': 'bg-red-100 text-red-800'
    };
    return colors[rating] || 'bg-gray-100 text-gray-800';
  };

  const getRiskLevelColor = (level: string) => {
    const colors: Record<string, string> = {
      'low': 'bg-green-100 text-green-800',
      'medium': 'bg-yellow-100 text-yellow-800',
      'high': 'bg-red-100 text-red-800'
    };
    return colors[level] || 'bg-gray-100 text-gray-800';
  };

  const getCurrencyIcon = (currency: string) => {
    const icons: Record<string, string> = {
      'USD': '💵',
      'EUR': '💶',
      'GBP': '💷',
      'SAR': '🇸🇦',
      'AED': '🇦🇪'
    };
    return icons[currency] || '💰';
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Credit Management Dashboard</h1>
        <p className="text-gray-600">Comprehensive credit risk management and counterparty exposure monitoring</p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', label: 'Credit Overview', icon: '📊' },
            { id: 'limits', label: 'Credit Limits', icon: '🏦' },
            { id: 'exposure', label: 'Exposure Management', icon: '⚠️' },
            { id: 'reports', label: 'Reports & Analytics', icon: '📈' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Credit Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Credit Dashboard Summary */}
          {dashboardData && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">Credit Risk Overview</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600">{dashboardData.total_counterparties}</div>
                  <div className="text-sm text-gray-600">Total Counterparties</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-orange-600">{formatCurrency(dashboardData.total_exposure)}</div>
                  <div className="text-sm text-gray-600">Total Exposure</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600">
                    {dashboardData.risk_distribution ? Object.keys(dashboardData.risk_distribution).length : 0}
                  </div>
                  <div className="text-sm text-gray-600">Risk Categories</div>
                </div>
              </div>

              {/* Risk Distribution Chart */}
              {dashboardData.risk_distribution && (
                <div className="mt-6">
                  <h3 className="text-lg font-medium mb-3">Risk Distribution</h3>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    {Object.entries(dashboardData.risk_distribution).map(([risk, count]) => (
                      <div key={risk} className="text-center p-4 bg-gray-50 rounded-lg">
                        <div className="text-2xl font-bold text-gray-900">{count as number}</div>
                        <div className="text-sm text-gray-600 capitalize">{risk} Risk</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button
                onClick={() => setActiveTab('limits')}
                className="p-4 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors"
              >
                <div className="text-center">
                  <div className="text-2xl mb-2">🏦</div>
                  <div className="font-medium text-blue-900">Set Credit Limit</div>
                  <div className="text-sm text-blue-600">Configure new credit limits</div>
                </div>
              </button>

              <button
                onClick={() => setActiveTab('exposure')}
                className="p-4 bg-orange-50 border border-orange-200 rounded-lg hover:bg-orange-100 transition-colors"
              >
                <div className="text-center">
                  <div className="text-2xl mb-2">⚠️</div>
                  <div className="font-medium text-orange-900">Calculate Exposure</div>
                  <div className="text-sm text-orange-600">Assess counterparty risk</div>
                </div>
              </button>

              <button
                onClick={handleGenerateCreditReport}
                disabled={loading}
                className="p-4 bg-green-50 border border-green-200 rounded-lg hover:bg-green-100 transition-colors disabled:opacity-50"
              >
                <div className="text-center">
                  <div className="text-2xl mb-2">📈</div>
                  <div className="font-medium text-green-900">Generate Report</div>
                  <div className="text-sm text-green-600">Create credit analysis</div>
                </div>
              </button>
            </div>
          </div>

          {/* Recent Credit Activities */}
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold">Recent Credit Activities</h3>
            </div>
            <div className="p-6">
              {creditLimits.length === 0 ? (
                <div className="text-center text-gray-500">
                  <p>No credit activities yet. Set credit limits to get started.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {creditLimits.slice(0, 5).map((limit, index) => (
                    <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-4">
                        <span className="text-2xl">{getCurrencyIcon(limit.currency)}</span>
                        <div>
                          <div className="font-medium">{limit.counterparty_id}</div>
                          <div className="text-sm text-gray-600">
                            Limit: {formatCurrency(limit.limit_amount)} {limit.currency}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <span className={`px-2 py-1 text-xs rounded-full ${getRiskRatingColor(limit.risk_rating)}`}>
                          {limit.risk_rating}
                        </span>
                        <div className="text-sm text-gray-600">
                          Expires: {new Date(limit.expiry_date).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Credit Limits Tab */}
      {activeTab === 'limits' && (
        <div className="space-y-6">
          {/* Set New Credit Limit */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Set New Credit Limit</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Counterparty ID</label>
                <input
                  type="text"
                  value={newCreditLimit.counterparty_id}
                  onChange={(e) => setNewCreditLimit(prev => ({ ...prev, counterparty_id: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="CP001"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Credit Limit Amount</label>
                <input
                  type="number"
                  value={newCreditLimit.limit_amount}
                  onChange={(e) => setNewCreditLimit(prev => ({ ...prev, limit_amount: parseFloat(e.target.value) }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="1000000"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Currency</label>
                <select
                  value={newCreditLimit.currency}
                  onChange={(e) => setNewCreditLimit(prev => ({ ...prev, currency: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="USD">USD</option>
                  <option value="EUR">EUR</option>
                  <option value="GBP">GBP</option>
                  <option value="SAR">SAR</option>
                  <option value="AED">AED</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Risk Rating</label>
                <select
                  value={newCreditLimit.risk_rating}
                  onChange={(e) => setNewCreditLimit(prev => ({ ...prev, risk_rating: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="A">A (Low Risk)</option>
                  <option value="B">B (Low-Medium Risk)</option>
                  <option value="C">C (Medium Risk)</option>
                  <option value="D">D (Medium-High Risk)</option>
                  <option value="E">E (High Risk)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Expiry Date</label>
                <input
                  type="date"
                  value={newCreditLimit.expiry_date}
                  onChange={(e) => setNewCreditLimit(prev => ({ ...prev, expiry_date: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div className="mt-6">
              <button
                onClick={handleSetCreditLimit}
                disabled={loading}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {loading ? 'Setting Credit Limit...' : 'Set Credit Limit'}
              </button>
            </div>
          </div>

          {/* Credit Limits Table */}
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold">Current Credit Limits</h3>
            </div>
            <div className="overflow-x-auto">
              {loading ? (
                <div className="p-6 text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                  <p className="mt-2 text-gray-600">Loading credit limits...</p>
                </div>
              ) : creditLimits.length === 0 ? (
                <div className="p-6 text-center text-gray-500">
                  <p>No credit limits found. Set a new credit limit to get started.</p>
                </div>
              ) : (
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Counterparty</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Credit Limit</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risk Rating</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Expiry Date</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {creditLimits.map((limit, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <span className="text-2xl mr-3">{getCurrencyIcon(limit.currency)}</span>
                            <div className="text-sm font-medium text-gray-900">{limit.counterparty_id}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatCurrency(limit.limit_amount)} {limit.currency}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRiskRatingColor(limit.risk_rating)}`}>
                            {limit.risk_rating}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(limit.expiry_date).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <button
                            onClick={() => handleCheckCreditAvailability(limit.counterparty_id, 100000)}
                            className="text-blue-600 hover:text-blue-900 mr-3"
                          >
                            Check Availability
                          </button>
                          <button
                            onClick={() => alert('Edit feature coming soon!')}
                            className="text-green-600 hover:text-green-900"
                          >
                            Edit
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Exposure Management Tab */}
      {activeTab === 'exposure' && (
        <div className="space-y-6">
          {/* Calculate Exposure */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Calculate Counterparty Exposure</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Counterparty ID</label>
                <input
                  type="text"
                  value={exposureCalculation.counterparty_id}
                  onChange={(e) => setExposureCalculation(prev => ({ ...prev, counterparty_id: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="CP001"
                />
              </div>
            </div>

            <div className="mt-4">
              <h3 className="text-lg font-medium mb-2">Position Data</h3>
              {exposureCalculation.positions.map((position, index) => (
                <div key={index} className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-2">
                  <input
                    type="text"
                    value={position.commodity}
                    onChange={(e) => {
                      const newPositions = [...exposureCalculation.positions];
                      newPositions[index].commodity = e.target.value;
                      setExposureCalculation(prev => ({ ...prev, positions: newPositions }));
                    }}
                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Commodity"
                  />
                  <input
                    type="number"
                    value={position.notional_value}
                    onChange={(e) => {
                      const newPositions = [...exposureCalculation.positions];
                      newPositions[index].notional_value = parseFloat(e.target.value);
                      setExposureCalculation(prev => ({ ...prev, positions: newPositions }));
                    }}
                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Notional Value"
                  />
                  <input
                    type="number"
                    value={position.mark_to_market}
                    onChange={(e) => {
                      const newPositions = [...exposureCalculation.positions];
                      newPositions[index].mark_to_market = parseFloat(e.target.value);
                      setExposureCalculation(prev => ({ ...prev, positions: newPositions }));
                    }}
                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Mark to Market"
                  />
                </div>
              ))}
              <button
                onClick={() => setExposureCalculation(prev => ({
                  ...prev,
                  positions: [...prev.positions, { commodity: '', notional_value: 0, mark_to_market: 0 }]
                }))}
                className="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Add Position
              </button>
            </div>

            <div className="mt-6">
              <button
                onClick={handleCalculateExposure}
                disabled={loading}
                className="w-full bg-orange-600 text-white py-2 px-4 rounded-md hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-orange-500 disabled:opacity-50"
              >
                {loading ? 'Calculating...' : 'Calculate Exposure'}
              </button>
            </div>
          </div>

          {/* Exposure Results */}
          {exposures.length > 0 && (
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold">Exposure Results</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Counterparty</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Current Exposure</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Available Credit</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Utilization</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risk Level</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {exposures.map((exposure, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {exposure.counterparty_id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatCurrency(exposure.current_exposure)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatCurrency(exposure.available_credit)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatPercentage(exposure.utilization_percentage)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRiskLevelColor(exposure.risk_level)}`}>
                            {exposure.risk_level}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Reports & Analytics Tab */}
      {activeTab === 'reports' && (
        <div className="space-y-6">
          {/* Report Generation */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Credit Reports & Analytics</h2>
            <p className="text-gray-600 mb-4">
              Generate comprehensive credit reports and analyze credit risk metrics across your portfolio.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-medium mb-3">Credit Report Generation</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Create detailed credit analysis reports including exposure calculations, risk assessments, and compliance checks.
                </p>
                <button
                  onClick={handleGenerateCreditReport}
                  disabled={loading}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  {loading ? 'Generating...' : 'Generate Credit Report'}
                </button>
              </div>

              <div>
                <h3 className="text-lg font-medium mb-3">Risk Analytics</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Analyze credit risk patterns, concentration risk, and portfolio-level exposure metrics.
                </p>
                <button
                  onClick={() => alert('Risk analytics dashboard coming soon!')}
                  className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  View Risk Analytics
                </button>
              </div>
            </div>
          </div>

          {/* Credit Metrics Summary */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Credit Metrics Summary</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{creditLimits.length}</div>
                <div className="text-sm text-gray-600">Active Limits</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {creditLimits.filter(l => l.risk_rating === 'A' || l.risk_rating === 'B').length}
                </div>
                <div className="text-sm text-gray-600">Low Risk</div>
              </div>
              <div className="text-center p-4 bg-yellow-50 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">
                  {creditLimits.filter(l => l.risk_rating === 'C').length}
                </div>
                <div className="text-sm text-gray-600">Medium Risk</div>
              </div>
              <div className="text-center p-4 bg-red-50 rounded-lg">
                <div className="text-2xl font-bold text-red-600">
                  {creditLimits.filter(l => l.risk_rating === 'D' || l.risk_rating === 'E').length}
                </div>
                <div className="text-sm text-gray-600">High Risk</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Summary Statistics */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <span className="text-2xl">🏦</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Credit Limits</p>
              <p className="text-2xl font-semibold text-gray-900">{creditLimits.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="p-2 bg-orange-100 rounded-lg">
              <span className="text-2xl">⚠️</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Exposures</p>
              <p className="text-2xl font-semibold text-gray-900">{exposures.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <span className="text-2xl">📊</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Limit Value</p>
              <p className="text-2xl font-semibold text-gray-900">
                {formatCurrency(creditLimits.reduce((sum, limit) => sum + limit.limit_amount, 0))}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <span className="text-2xl">📈</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Dashboard</p>
              <p className="text-2xl font-semibold text-gray-900">{dashboardData ? 'Updated' : 'Pending'}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreditManagementDashboard;
