import React, { useState, useEffect } from 'react';
import {
  calculateVaRMonteCarlo,
  calculateVaRParametric,
  calculateVaRHistorical,
  stressTestPortfolio,
  calculateExpectedShortfall,
  performScenarioAnalysis,
  generateRiskReport,
  getRiskMetrics,
  getRiskDashboard,
  runMonteCarloSimulation,
  getSimulationStatus,
  getSimulationResults,
  PortfolioData,
  RiskMetrics,
  formatCurrency,
  formatPercentage
} from '../services/tradingApi';

interface RiskAnalyticsDashboardProps {
  userId?: string;
}

const RiskAnalyticsDashboard: React.FC<RiskAnalyticsDashboardProps> = ({ userId = 'user123' }) => {
  // State management
  const [portfolioData, setPortfolioData] = useState<PortfolioData>({
    portfolio_id: 'portfolio_001',
    total_value: 1000000.0,
    volatility: 0.15,
    positions: [
      { commodity: 'crude_oil', quantity: 1000, price: 85.50 },
      { commodity: 'natural_gas', quantity: 5000, price: 3.20 },
      { commodity: 'electricity', quantity: 2000, price: 42.00 },
      { commodity: 'coal', quantity: 500, price: 110.00 }
    ],
    historical_returns: [0.01, -0.02, 0.015, -0.01, 0.02, -0.005, 0.018, -0.012, 0.025, -0.008]
  });

  const [riskMetrics, setRiskMetrics] = useState<RiskMetrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'var' | 'stress' | 'simulation'>('overview');
  const [simulationId, setSimulationId] = useState<string | null>(null);
  const [simulationStatus, setSimulationStatus] = useState<string>('idle');

  // VaR calculation parameters
  const [varParams, setVarParams] = useState({
    confidenceLevel: 0.95,
    timeHorizon: 1,
    numSimulations: 10000,
    historicalPeriod: 252
  });

  // Stress test scenarios
  const [stressScenarios, setStressScenarios] = useState([
    { name: 'Oil Price Crash', type: 'market_shock', shock_factor: 0.3 },
    { name: 'Volatility Spike', type: 'volatility_spike', spike_factor: 2.5 },
    { name: 'Interest Rate Hike', type: 'rate_shock', shock_factor: 0.5 },
    { name: 'Geopolitical Crisis', type: 'market_shock', shock_factor: 0.4 }
  ]);

  // Load risk metrics on component mount
  useEffect(() => {
    loadRiskMetrics();
  }, []);

  const loadRiskMetrics = async () => {
    try {
      setLoading(true);
      const metrics = await getRiskMetrics();
      if (metrics.success) {
        setRiskMetrics(metrics.data);
      }
    } catch (err) {
      setError('Failed to load risk metrics');
      console.error('Error loading risk metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleVaRCalculation = async (method: 'monte_carlo' | 'parametric' | 'historical') => {
    try {
      setLoading(true);
      setError(null);
      
      let result;
      switch (method) {
        case 'monte_carlo':
          result = await calculateVaRMonteCarlo(
            portfolioData,
            varParams.confidenceLevel,
            varParams.timeHorizon,
            varParams.numSimulations
          );
          break;
        case 'parametric':
          result = await calculateVaRParametric(
            portfolioData,
            varParams.confidenceLevel,
            varParams.timeHorizon
          );
          break;
        case 'historical':
          result = await calculateVaRHistorical(
            portfolioData,
            varParams.confidenceLevel,
            varParams.timeHorizon,
            varParams.historicalPeriod
          );
          break;
      }
      
      if (result.success) {
        alert(`${method.replace('_', ' ').toUpperCase()} VaR calculation completed successfully!`);
        await loadRiskMetrics(); // Refresh metrics
      }
    } catch (err) {
      setError(`Failed to calculate ${method.replace('_', ' ')} VaR`);
      console.error(`Error calculating ${method} VaR:`, err);
    } finally {
      setLoading(false);
    }
  };

  const handleStressTest = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await stressTestPortfolio(portfolioData, stressScenarios);
      
      if (result.success) {
        alert('Stress testing completed successfully!');
        await loadRiskMetrics(); // Refresh metrics
      }
    } catch (err) {
      setError('Failed to perform stress testing');
      console.error('Error performing stress testing:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExpectedShortfall = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await calculateExpectedShortfall(
        portfolioData,
        varParams.confidenceLevel,
        varParams.timeHorizon
      );
      
      if (result.success) {
        alert('Expected Shortfall calculation completed successfully!');
        await loadRiskMetrics(); // Refresh metrics
      }
    } catch (err) {
      setError('Failed to calculate Expected Shortfall');
      console.error('Error calculating Expected Shortfall:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleScenarioAnalysis = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await performScenarioAnalysis(portfolioData, stressScenarios);
      
      if (result.success) {
        alert(`Scenario analysis completed! Analyzed ${result.data.scenarios_analyzed} scenarios.`);
        await loadRiskMetrics(); // Refresh metrics
      }
    } catch (err) {
      setError('Failed to perform scenario analysis');
      console.error('Error performing scenario analysis:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleMonteCarloSimulation = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const simulationParams = {
        positions: portfolioData.positions.map(pos => ({
          commodity: pos.commodity,
          notional_value: pos.quantity * pos.price,
          expected_return: 0.05,
          volatility: 0.2
        })),
        market_data: {},
        correlations: {},
        num_simulations: varParams.numSimulations,
        time_horizon: varParams.timeHorizon
      };
      
      const result = await runMonteCarloSimulation(simulationParams);
      
      if (result.success) {
        setSimulationId(result.data.simulation_id);
        setSimulationStatus('running');
        alert('Monte Carlo simulation started! Check status for updates.');
      }
    } catch (err) {
      setError('Failed to start Monte Carlo simulation');
      console.error('Error starting Monte Carlo simulation:', err);
    } finally {
      setLoading(false);
    }
  };

  const checkSimulationStatus = async () => {
    if (!simulationId) return;
    
    try {
      const result = await getSimulationStatus(simulationId);
      if (result.success) {
        setSimulationStatus(result.data.status);
        
        if (result.data.status === 'completed') {
          // Get results
          const results = await getSimulationResults(simulationId);
          if (results.success) {
            alert(`Simulation completed! VaR: ${formatCurrency(results.data.var_95)}, ES: ${formatCurrency(results.data.expected_shortfall)}`);
            await loadRiskMetrics(); // Refresh metrics
          }
        }
      }
    } catch (err) {
      console.error('Error checking simulation status:', err);
    }
  };

  const getCommodityIcon = (commodity: string) => {
    const icons: Record<string, string> = {
      crude_oil: '🛢️',
      natural_gas: '🔥',
      electricity: '⚡',
      renewables: '🌱',
      carbon_credits: '🌍',
      coal: '⛏️',
      lng: '🚢',
      lpg: '🏭'
    };
    return icons[commodity] || '📦';
  };

  const getRiskLevelColor = (level: string) => {
    const colors: Record<string, string> = {
      low: 'bg-green-100 text-green-800',
      medium: 'bg-yellow-100 text-yellow-800',
      high: 'bg-red-100 text-red-800'
    };
    return colors[level] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Risk Analytics Dashboard</h1>
        <p className="text-gray-600">Comprehensive risk management and analytics for your portfolio</p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', label: 'Risk Overview', icon: '📊' },
            { id: 'var', label: 'VaR Analysis', icon: '📈' },
            { id: 'stress', label: 'Stress Testing', icon: '⚡' },
            { id: 'simulation', label: 'Monte Carlo', icon: '🎲' }
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

      {/* Risk Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Portfolio Summary */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Portfolio Summary</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600">{formatCurrency(portfolioData.total_value)}</div>
                <div className="text-sm text-gray-600">Total Portfolio Value</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-orange-600">{formatPercentage(portfolioData.volatility)}</div>
                <div className="text-sm text-gray-600">Portfolio Volatility</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">{portfolioData.positions.length}</div>
                <div className="text-sm text-gray-600">Active Positions</div>
              </div>
            </div>
          </div>

          {/* Portfolio Positions */}
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold">Portfolio Positions</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Commodity</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quantity</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Market Value</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Weight</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {portfolioData.positions.map((position, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <span className="text-2xl mr-3">{getCommodityIcon(position.commodity)}</span>
                          <div className="text-sm font-medium text-gray-900 capitalize">
                            {position.commodity.replace('_', ' ')}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {position.quantity.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatCurrency(position.price)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatCurrency(position.quantity * position.price)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatPercentage((position.quantity * position.price) / portfolioData.total_value)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Risk Metrics */}
          {riskMetrics && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">Current Risk Metrics</h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{formatCurrency(riskMetrics.var_95)}</div>
                  <div className="text-sm text-gray-600">VaR (95%)</div>
                </div>
                <div className="text-center p-4 bg-red-50 rounded-lg">
                  <div className="text-2xl font-bold text-red-600">{formatCurrency(riskMetrics.var_99)}</div>
                  <div className="text-sm text-gray-600">VaR (99%)</div>
                </div>
                <div className="text-center p-4 bg-orange-50 rounded-lg">
                  <div className="text-2xl font-bold text-orange-600">{formatCurrency(riskMetrics.expected_shortfall)}</div>
                  <div className="text-sm text-gray-600">Expected Shortfall</div>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-sm text-gray-600">Last Updated</div>
                  <div className="text-sm font-medium text-gray-900">
                    {new Date(riskMetrics.calculated_at).toLocaleDateString()}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* VaR Analysis Tab */}
      {activeTab === 'var' && (
        <div className="space-y-6">
          {/* VaR Parameters */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">VaR Calculation Parameters</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Confidence Level</label>
                <select
                  value={varParams.confidenceLevel}
                  onChange={(e) => setVarParams(prev => ({ ...prev, confidenceLevel: parseFloat(e.target.value) }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value={0.90}>90%</option>
                  <option value={0.95}>95%</option>
                  <option value={0.99}>99%</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Time Horizon (Days)</label>
                <input
                  type="number"
                  value={varParams.timeHorizon}
                  onChange={(e) => setVarParams(prev => ({ ...prev, timeHorizon: parseInt(e.target.value) }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  min="1"
                  max="30"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Simulations</label>
                <input
                  type="number"
                  value={varParams.numSimulations}
                  onChange={(e) => setVarParams(prev => ({ ...prev, numSimulations: parseInt(e.target.value) }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  min="1000"
                  max="100000"
                  step="1000"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Historical Period</label>
                <input
                  type="number"
                  value={varParams.historicalPeriod}
                  onChange={(e) => setVarParams(prev => ({ ...prev, historicalPeriod: parseInt(e.target.value) }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  min="30"
                  max="1000"
                />
              </div>
            </div>

            <div className="mt-6 flex space-x-4">
              <button
                onClick={() => handleVaRCalculation('monte_carlo')}
                disabled={loading}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {loading ? 'Calculating...' : 'Calculate Monte Carlo VaR'}
              </button>
              <button
                onClick={() => handleVaRCalculation('parametric')}
                disabled={loading}
                className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
              >
                {loading ? 'Calculating...' : 'Calculate Parametric VaR'}
              </button>
              <button
                onClick={() => handleVaRCalculation('historical')}
                disabled={loading}
                className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50"
              >
                {loading ? 'Calculating...' : 'Calculate Historical VaR'}
              </button>
            </div>
          </div>

          {/* Expected Shortfall */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Expected Shortfall (Conditional VaR)</h3>
            <p className="text-gray-600 mb-4">
              Expected Shortfall measures the expected loss given that the loss exceeds the VaR threshold.
            </p>
            <button
              onClick={handleExpectedShortfall}
              disabled={loading}
              className="bg-orange-600 text-white px-4 py-2 rounded hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-orange-500 disabled:opacity-50"
            >
              {loading ? 'Calculating...' : 'Calculate Expected Shortfall'}
            </button>
          </div>
        </div>
      )}

      {/* Stress Testing Tab */}
      {activeTab === 'stress' && (
        <div className="space-y-6">
          {/* Stress Scenarios */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Stress Test Scenarios</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              {stressScenarios.map((scenario, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium">{scenario.name}</h4>
                    <span className={`px-2 py-1 text-xs rounded-full ${getRiskLevelColor(scenario.type === 'volatility_spike' ? 'high' : 'medium')}`}>
                      {scenario.type.replace('_', ' ')}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600">
                    Factor: {scenario.shock_factor ? `${(scenario.shock_factor * 100).toFixed(0)}%` : `${(scenario.spike_factor || 0).toFixed(1)}x`}
                  </div>
                </div>
              ))}
            </div>

            <div className="flex space-x-4">
              <button
                onClick={handleStressTest}
                disabled={loading}
                className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 disabled:opacity-50"
              >
                {loading ? 'Testing...' : 'Run Stress Test'}
              </button>
              <button
                onClick={handleScenarioAnalysis}
                disabled={loading}
                className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
              >
                {loading ? 'Analyzing...' : 'Scenario Analysis'}
              </button>
            </div>
          </div>

          {/* Risk Report Generation */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Generate Risk Report</h3>
            <p className="text-gray-600 mb-4">
              Generate comprehensive risk reports including VaR, stress testing, and scenario analysis results.
            </p>
            <button
              onClick={() => alert('Risk report generation feature coming soon!')}
              className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              Generate Risk Report
            </button>
          </div>
        </div>
      )}

      {/* Monte Carlo Simulation Tab */}
      {activeTab === 'simulation' && (
        <div className="space-y-6">
          {/* Simulation Control */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Monte Carlo Simulation</h2>
            <p className="text-gray-600 mb-4">
              Run Monte Carlo simulations to assess portfolio risk under various market scenarios.
            </p>
            
            <div className="mb-6">
              <h3 className="text-lg font-medium mb-2">Simulation Parameters</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Number of Simulations</label>
                  <input
                    type="number"
                    value={varParams.numSimulations}
                    onChange={(e) => setVarParams(prev => ({ ...prev, numSimulations: parseInt(e.target.value) }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    min="1000"
                    max="100000"
                    step="1000"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Time Horizon (Days)</label>
                  <input
                    type="number"
                    value={varParams.timeHorizon}
                    onChange={(e) => setVarParams(prev => ({ ...prev, timeHorizon: parseInt(e.target.value) }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    min="1"
                    max="30"
                  />
                </div>
              </div>
            </div>

            <div className="flex space-x-4">
              <button
                onClick={handleMonteCarloSimulation}
                disabled={loading || simulationStatus === 'running'}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {loading ? 'Starting...' : 'Start Simulation'}
              </button>
              {simulationId && (
                <button
                  onClick={checkSimulationStatus}
                  className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  Check Status
                </button>
              )}
            </div>

            {/* Simulation Status */}
            {simulationId && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium mb-2">Simulation Status</h4>
                <div className="flex items-center space-x-4">
                  <div className="text-sm">
                    <span className="font-medium">ID:</span> {simulationId}
                  </div>
                  <div className="text-sm">
                    <span className="font-medium">Status:</span> 
                    <span className={`ml-2 px-2 py-1 text-xs rounded-full ${
                      simulationStatus === 'running' ? 'bg-yellow-100 text-yellow-800' :
                      simulationStatus === 'completed' ? 'bg-green-100 text-green-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {simulationStatus}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Simulation Results */}
          {simulationStatus === 'completed' && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">Simulation Results</h3>
              <p className="text-gray-600 mb-4">
                Monte Carlo simulation completed successfully. Results have been integrated into your risk metrics.
              </p>
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-green-800">
                      Simulation completed! Check the Risk Overview tab for updated metrics.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Summary Statistics */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <span className="text-2xl">📊</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Portfolio Value</p>
              <p className="text-2xl font-semibold text-gray-900">{formatCurrency(portfolioData.total_value)}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-lg">
              <span className="text-2xl">⚠️</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Portfolio Volatility</p>
              <p className="text-2xl font-semibold text-gray-900">{formatPercentage(portfolioData.volatility)}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <span className="text-2xl">🎯</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Positions</p>
              <p className="text-2xl font-semibold text-gray-900">{portfolioData.positions.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <span className="text-2xl">📈</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Risk Metrics</p>
              <p className="text-2xl font-semibold text-gray-900">{riskMetrics ? 'Updated' : 'Pending'}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskAnalyticsDashboard;
