import React, { useState, useEffect } from 'react';
import {
  executeAlgorithm,
  calculateVWAP,
  executeTWAPStrategy,
  optimizeOrderSizing,
  monitorExecutionQuality,
  getStrategyPerformance,
  validateAlgoStrategy,
  checkExecutionEthics,
  AlgoStrategyCreate,
  formatCurrency,
  formatPercentage
} from '../services/tradingApi';

interface AlgorithmicTradingDashboardProps {
  userId?: string;
}

const AlgorithmicTradingDashboard: React.FC<AlgorithmicTradingDashboardProps> = ({ userId = 'user123' }) => {
  // State management
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'strategies' | 'execution' | 'monitoring' | 'compliance'>('strategies');
  const [executionHistory, setExecutionHistory] = useState<any[]>([]);
  const [strategyPerformance, setStrategyPerformance] = useState<any>(null);

  // Algorithm strategy form state
  const [algoStrategy, setAlgoStrategy] = useState<AlgoStrategyCreate>({
    strategy_name: 'TWAP Strategy',
    strategy_type: 'twap',
    parameters: {
      total_quantity: 1000000.0,
      duration_minutes: 60,
      slice_interval: 5,
      commodity: 'crude_oil',
      execution_type: 'buy'
    },
    risk_limits: {
      max_order_size: 1000000.0,
      max_daily_volume: 10000000.0,
      max_slippage: 0.02
    },
    islamic_compliant: true,
    execution_mode: 'passive'
  });

  // TWAP strategy parameters
  const [twapParams, setTwapParams] = useState({
    total_quantity: 1000000.0,
    duration_minutes: 60,
    slice_interval: 5,
    commodity: 'crude_oil',
    execution_type: 'buy'
  });

  // VWAP calculation parameters
  const [vwapOrders, setVwapOrders] = useState([
    { price: 85.50, volume: 100000 },
    { price: 85.60, volume: 150000 },
    { price: 85.45, volume: 200000 }
  ]);

  // Order sizing optimization parameters
  const [orderSizingParams, setOrderSizingParams] = useState({
    market_data: { volatility: 0.02, liquidity: 'high' },
    target_volume: 500000.0,
    risk_params: { max_position_size: 1000000, risk_tolerance: 0.05 }
  });

  // Load initial data
  useEffect(() => {
    loadStrategyPerformance();
  }, []);

  const loadStrategyPerformance = async () => {
    try {
      const performance = await getStrategyPerformance('twap', '1M');
      if (performance.status === 'success') {
        setStrategyPerformance(performance.data);
      }
    } catch (err) {
      console.error('Error loading strategy performance:', err);
    }
  };

  const handleExecuteAlgorithm = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await executeAlgorithm(algoStrategy);
      
      if (result.status === 'success') {
        // Add to execution history
        setExecutionHistory(prev => [{
          id: result.data.execution_id,
          strategy: result.data.strategy,
          timestamp: new Date().toISOString(),
          status: 'executed'
        }, ...prev]);
        
        alert('Algorithm executed successfully!');
      }
    } catch (err) {
      setError('Failed to execute algorithm');
      console.error('Error executing algorithm:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteTWAP = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await executeTWAPStrategy(twapParams);
      
      if (result.status === 'success') {
        // Add to execution history
        setExecutionHistory(prev => [{
          id: result.data.strategy_id,
          strategy: 'TWAP',
          timestamp: new Date().toISOString(),
          status: 'executing',
          details: result.data
        }, ...prev]);
        
        alert('TWAP strategy initiated successfully!');
      }
    } catch (err) {
      setError('Failed to execute TWAP strategy');
      console.error('Error executing TWAP strategy:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCalculateVWAP = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await calculateVWAP(vwapOrders, '1D');
      
      if (result.status === 'success') {
        alert(`VWAP calculated: ${formatCurrency(result.data.vwap)}`);
      }
    } catch (err) {
      setError('Failed to calculate VWAP');
      console.error('Error calculating VWAP:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleOptimizeOrderSizing = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await optimizeOrderSizing(
        orderSizingParams.market_data,
        orderSizingParams.target_volume,
        orderSizingParams.risk_params
      );
      
      if (result.status === 'success') {
        alert(`Order sizing optimized! Optimal slice size: ${formatCurrency(result.data.optimal_slice_size)}`);
      }
    } catch (err) {
      setError('Failed to optimize order sizing');
      console.error('Error optimizing order sizing:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleValidateStrategy = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await validateAlgoStrategy({
        strategy: algoStrategy.strategy_type,
        risk_controls: ['position_limits', 'volatility_checks'],
        execution_params: { max_slippage: algoStrategy.risk_limits.max_slippage }
      });
      
      if (result.status === 'success') {
        alert(`Strategy validation: ${result.data.islamic_compliant ? 'Compliant' : 'Non-compliant'} (Score: ${result.data.compliance_score})`);
      }
    } catch (err) {
      setError('Failed to validate strategy');
      console.error('Error validating strategy:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckExecutionEthics = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await checkExecutionEthics({
        execution_id: 'EXE_20240115_100000',
        market_impact: 0.001,
        execution_time: new Date().toISOString()
      });
      
      if (result.status === 'success') {
        alert(`Execution ethics: ${result.data.ethical_execution ? 'Ethical' : 'Questionable'} (Fairness: ${(result.data.fairness_score * 100).toFixed(1)}%)`);
      }
    } catch (err) {
      setError('Failed to check execution ethics');
      console.error('Error checking execution ethics:', err);
    } finally {
      setLoading(false);
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

  const getExecutionStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      executing: 'bg-yellow-100 text-yellow-800',
      executed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
      pending: 'bg-blue-100 text-blue-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Algorithmic Trading Dashboard</h1>
        <p className="text-gray-600">Advanced algorithmic trading strategies with Islamic compliance</p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'strategies', label: 'Strategy Builder', icon: '🏗️' },
            { id: 'execution', label: 'Execution', icon: '⚡' },
            { id: 'monitoring', label: 'Monitoring', icon: '📊' },
            { id: 'compliance', label: 'Compliance', icon: '☪️' }
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

      {/* Strategy Builder Tab */}
      {activeTab === 'strategies' && (
        <div className="space-y-6">
          {/* Algorithm Strategy Builder */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Algorithm Strategy Builder</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Strategy Name</label>
                <input
                  type="text"
                  value={algoStrategy.strategy_name}
                  onChange={(e) => setAlgoStrategy(prev => ({ ...prev, strategy_name: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="My Strategy"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Strategy Type</label>
                <select
                  value={algoStrategy.strategy_type}
                  onChange={(e) => setAlgoStrategy(prev => ({ ...prev, strategy_type: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="twap">TWAP</option>
                  <option value="vwap">VWAP</option>
                  <option value="iceberg">Iceberg</option>
                  <option value="smart_order_routing">Smart Order Routing</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Execution Mode</label>
                <select
                  value={algoStrategy.execution_mode}
                  onChange={(e) => setAlgoStrategy(prev => ({ ...prev, execution_mode: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="passive">Passive</option>
                  <option value="aggressive">Aggressive</option>
                  <option value="adaptive">Adaptive</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Islamic Compliant</label>
                <select
                  value={algoStrategy.islamic_compliant.toString()}
                  onChange={(e) => setAlgoStrategy(prev => ({ ...prev, islamic_compliant: e.target.value === 'true' }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="true">Yes</option>
                  <option value="false">No</option>
                </select>
              </div>
            </div>

            <div className="mt-6">
              <h3 className="text-lg font-medium mb-3">Risk Limits</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Max Order Size</label>
                  <input
                    type="number"
                    value={algoStrategy.risk_limits.max_order_size}
                    onChange={(e) => setAlgoStrategy(prev => ({
                      ...prev,
                      risk_limits: { ...prev.risk_limits, max_order_size: parseFloat(e.target.value) }
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="1000000"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Max Daily Volume</label>
                  <input
                    type="number"
                    value={algoStrategy.risk_limits.max_daily_volume}
                    onChange={(e) => setAlgoStrategy(prev => ({
                      ...prev,
                      risk_limits: { ...prev.risk_limits, max_daily_volume: parseFloat(e.target.value) }
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="10000000"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Max Slippage</label>
                  <input
                    type="number"
                    step="0.001"
                    value={algoStrategy.risk_limits.max_slippage}
                    onChange={(e) => setAlgoStrategy(prev => ({
                      ...prev,
                      risk_limits: { ...prev.risk_limits, max_slippage: parseFloat(e.target.value) }
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="0.02"
                  />
                </div>
              </div>
            </div>

            <div className="mt-6">
              <button
                onClick={handleExecuteAlgorithm}
                disabled={loading}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {loading ? 'Executing...' : 'Execute Algorithm'}
              </button>
            </div>
          </div>

          {/* TWAP Strategy Builder */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">TWAP Strategy Builder</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Total Quantity</label>
                <input
                  type="number"
                  value={twapParams.total_quantity}
                  onChange={(e) => setTwapParams(prev => ({ ...prev, total_quantity: parseFloat(e.target.value) }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="1000000"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Duration (Minutes)</label>
                <input
                  type="number"
                  value={twapParams.duration_minutes}
                  onChange={(e) => setTwapParams(prev => ({ ...prev, duration_minutes: parseInt(e.target.value) }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="60"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Slice Interval (Minutes)</label>
                <input
                  type="number"
                  value={twapParams.slice_interval}
                  onChange={(e) => setTwapParams(prev => ({ ...prev, slice_interval: parseInt(e.target.value) }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="5"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Commodity</label>
                <select
                  value={twapParams.commodity}
                  onChange={(e) => setTwapParams(prev => ({ ...prev, commodity: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="crude_oil">Crude Oil</option>
                  <option value="natural_gas">Natural Gas</option>
                  <option value="electricity">Electricity</option>
                  <option value="renewables">Renewables</option>
                  <option value="carbon_credits">Carbon Credits</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Execution Type</label>
                <select
                  value={twapParams.execution_type}
                  onChange={(e) => setTwapParams(prev => ({ ...prev, execution_type: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="buy">Buy</option>
                  <option value="sell">Sell</option>
                </select>
              </div>
            </div>

            <div className="mt-6">
              <button
                onClick={handleExecuteTWAP}
                disabled={loading}
                className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
              >
                {loading ? 'Executing...' : 'Execute TWAP Strategy'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Execution Tab */}
      {activeTab === 'execution' && (
        <div className="space-y-6">
          {/* VWAP Calculator */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">VWAP Calculator</h2>
            <div className="mb-4">
              <h3 className="text-lg font-medium mb-2">Order Book</h3>
              {vwapOrders.map((order, index) => (
                <div key={index} className="flex space-x-4 mb-2">
                  <input
                    type="number"
                    step="0.01"
                    value={order.price}
                    onChange={(e) => {
                      const newOrders = [...vwapOrders];
                      newOrders[index].price = parseFloat(e.target.value);
                      setVwapOrders(newOrders);
                    }}
                    className="w-32 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Price"
                  />
                  <input
                    type="number"
                    value={order.volume}
                    onChange={(e) => {
                      const newOrders = [...vwapOrders];
                      newOrders[index].volume = parseInt(e.target.value);
                      setVwapOrders(newOrders);
                    }}
                    className="w-32 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Volume"
                  />
                  <button
                    onClick={() => setVwapOrders(prev => prev.filter((_, i) => i !== index))}
                    className="px-3 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                  >
                    Remove
                  </button>
                </div>
              ))}
              <button
                onClick={() => setVwapOrders(prev => [...prev, { price: 0, volume: 0 }])}
                className="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Add Order
              </button>
            </div>

            <button
              onClick={handleCalculateVWAP}
              disabled={loading}
              className="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50"
            >
              {loading ? 'Calculating...' : 'Calculate VWAP'}
            </button>
          </div>

          {/* Order Sizing Optimization */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Order Sizing Optimization</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Market Volatility</label>
                <input
                  type="number"
                  step="0.001"
                  value={orderSizingParams.market_data.volatility}
                  onChange={(e) => setOrderSizingParams(prev => ({
                    ...prev,
                    market_data: { ...prev.market_data, volatility: parseFloat(e.target.value) }
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0.02"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Market Liquidity</label>
                <select
                  value={orderSizingParams.market_data.liquidity}
                  onChange={(e) => setOrderSizingParams(prev => ({
                    ...prev,
                    market_data: { ...prev.market_data, liquidity: e.target.value }
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Target Volume</label>
                <input
                  type="number"
                  value={orderSizingParams.target_volume}
                  onChange={(e) => setOrderSizingParams(prev => ({ ...prev, target_volume: parseFloat(e.target.value) }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="500000"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Risk Tolerance</label>
                <input
                  type="number"
                  step="0.001"
                  value={orderSizingParams.risk_params.risk_tolerance}
                  onChange={(e) => setOrderSizingParams(prev => ({
                    ...prev,
                    risk_params: { ...prev.risk_params, risk_tolerance: parseFloat(e.target.value) }
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0.05"
                />
              </div>
            </div>

            <div className="mt-6">
              <button
                onClick={handleOptimizeOrderSizing}
                disabled={loading}
                className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
              >
                {loading ? 'Optimizing...' : 'Optimize Order Sizing'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Monitoring Tab */}
      {activeTab === 'monitoring' && (
        <div className="space-y-6">
          {/* Execution History */}
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold">Execution History</h2>
            </div>
            <div className="overflow-x-auto">
              {executionHistory.length === 0 ? (
                <div className="p-6 text-center text-gray-500">
                  <p>No executions yet. Execute a strategy to see history.</p>
                </div>
              ) : (
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Execution ID</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Strategy</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Timestamp</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {executionHistory.map((execution) => (
                      <tr key={execution.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {execution.id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {execution.strategy}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getExecutionStatusColor(execution.status)}`}>
                            {execution.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(execution.timestamp).toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <button
                            onClick={() => alert('Execution quality monitoring coming soon!')}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            Monitor Quality
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>

          {/* Strategy Performance */}
          {strategyPerformance && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">Strategy Performance</h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{strategyPerformance.total_trades}</div>
                  <div className="text-sm text-gray-600">Total Trades</div>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">{formatPercentage(strategyPerformance.win_rate)}</div>
                  <div className="text-sm text-gray-600">Win Rate</div>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">{strategyPerformance.profit_factor}</div>
                  <div className="text-sm text-gray-600">Profit Factor</div>
                </div>
                <div className="text-center p-4 bg-orange-50 rounded-lg">
                  <div className="text-2xl font-bold text-orange-600">{strategyPerformance.sharpe_ratio}</div>
                  <div className="text-sm text-gray-600">Sharpe Ratio</div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Compliance Tab */}
      {activeTab === 'compliance' && (
        <div className="space-y-6">
          {/* Strategy Validation */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Strategy Compliance Validation</h2>
            <p className="text-gray-600 mb-4">
              Validate your algorithmic trading strategies for Islamic compliance and ethical execution.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-medium mb-3">Strategy Validation</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Check if your strategy meets Islamic trading requirements and compliance standards.
                </p>
                <button
                  onClick={handleValidateStrategy}
                  disabled={loading}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  {loading ? 'Validating...' : 'Validate Strategy'}
                </button>
              </div>

              <div>
                <h3 className="text-lg font-medium mb-3">Execution Ethics Check</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Assess the ethical implications and market impact of your execution strategy.
                </p>
                <button
                  onClick={handleCheckExecutionEthics}
                  disabled={loading}
                  className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
                >
                  {loading ? 'Checking...' : 'Check Execution Ethics'}
                </button>
              </div>
            </div>
          </div>

          {/* Compliance Guidelines */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Islamic Trading Compliance Guidelines</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-green-700 mb-2">✅ Permitted Practices</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Asset-backed trading</li>
                  <li>• Risk-sharing arrangements</li>
                  <li>• Transparent pricing</li>
                  <li>• Ethical market behavior</li>
                  <li>• Avoidance of excessive speculation</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-red-700 mb-2">❌ Prohibited Practices</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Interest-based transactions (Riba)</li>
                  <li>• Excessive uncertainty (Gharar)</li>
                  <li>• Market manipulation</li>
                  <li>• Gambling-like speculation</li>
                  <li>• Trading in prohibited assets</li>
                </ul>
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
              <span className="text-2xl">📊</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Executions</p>
              <p className="text-2xl font-semibold text-gray-900">{executionHistory.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <span className="text-2xl">✅</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Successful</p>
              <p className="text-2xl font-semibold text-gray-900">
                {executionHistory.filter(e => e.status === 'executed').length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <span className="text-2xl">⏳</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">In Progress</p>
              <p className="text-2xl font-semibold text-gray-900">
                {executionHistory.filter(e => e.status === 'executing').length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <span className="text-2xl">☪️</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Islamic Compliant</p>
              <p className="text-2xl font-semibold text-gray-900">
                {algoStrategy.islamic_compliant ? 'Yes' : 'No'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AlgorithmicTradingDashboard;
