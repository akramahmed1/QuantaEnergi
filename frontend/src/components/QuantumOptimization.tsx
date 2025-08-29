import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import axios from 'axios';

interface PortfolioAsset {
  symbol: string;
  name: string;
  current_weight: number;
  optimized_weight: number;
  expected_return: number;
  risk_score: number;
}

interface OptimizationResult {
  portfolio_assets: PortfolioAsset[];
  expected_return: number;
  risk_score: number;
  sharpe_ratio: number;
  quantum_advantage: number;
  classical_fallback: boolean;
  execution_time: number;
}

interface RiskAssessment {
  market_risk: number;
  credit_risk: number;
  liquidity_risk: number;
  operational_risk: number;
  quantum_risk: number;
  overall_risk: number;
}

const QuantumOptimization: React.FC = () => {
  const [optimizationResult, setOptimizationResult] = useState<OptimizationResult | null>(null);
  const [riskAssessment, setRiskAssessment] = useState<RiskAssessment | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedAlgorithm, setSelectedAlgorithm] = useState('qaoa');
  const [riskTolerance, setRiskTolerance] = useState(0.5);
  const [targetReturn, setTargetReturn] = useState(0.12);

  const generateMockPortfolioAssets = (): PortfolioAsset[] => [
    { symbol: 'SOL', name: 'Solar Energy ETF', current_weight: 0.25, optimized_weight: 0.30, expected_return: 0.15, risk_score: 0.08 },
    { symbol: 'WIND', name: 'Wind Energy ETF', current_weight: 0.20, optimized_weight: 0.25, expected_return: 0.12, risk_score: 0.10 },
    { symbol: 'BAT', name: 'Battery Storage ETF', current_weight: 0.15, optimized_weight: 0.20, expected_return: 0.18, risk_score: 0.12 },
    { symbol: 'GRID', name: 'Smart Grid ETF', current_weight: 0.20, optimized_weight: 0.15, expected_return: 0.10, risk_score: 0.06 },
    { symbol: 'CARB', name: 'Carbon Credits ETF', current_weight: 0.20, optimized_weight: 0.10, expected_return: 0.08, risk_score: 0.04 },
  ];

  const generateMockOptimizationResult = (): OptimizationResult => ({
    portfolio_assets: generateMockPortfolioAssets(),
    expected_return: 0.13 + Math.random() * 0.04,
    risk_score: 0.08 + Math.random() * 0.04,
    sharpe_ratio: 1.2 + Math.random() * 0.6,
    quantum_advantage: 0.15 + Math.random() * 0.10,
    classical_fallback: Math.random() > 0.7,
    execution_time: 0.5 + Math.random() * 2.0,
  });

  const generateMockRiskAssessment = (): RiskAssessment => ({
    market_risk: 0.12 + Math.random() * 0.08,
    credit_risk: 0.08 + Math.random() * 0.06,
    liquidity_risk: 0.06 + Math.random() * 0.04,
    operational_risk: 0.04 + Math.random() * 0.03,
    quantum_risk: 0.02 + Math.random() * 0.02,
    overall_risk: 0.08 + Math.random() * 0.05,
  });

  useEffect(() => {
    // Load mock data initially
    setOptimizationResult(generateMockOptimizationResult());
    setRiskAssessment(generateMockRiskAssessment());
  }, []);

  const handleOptimizationRequest = async () => {
    setLoading(true);
    try {
      // In production, this would call the actual backend API
      // const response = await axios.post('/api/disruptive/quantum/optimize', {
      //   algorithm: selectedAlgorithm,
      //   risk_tolerance: riskTolerance,
      //   target_return: targetReturn,
      // });
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Update with new mock data
      setOptimizationResult(generateMockOptimizationResult());
      setRiskAssessment(generateMockRiskAssessment());
      
      toast.success('Quantum optimization completed successfully!');
    } catch (error) {
      toast.error('Failed to complete optimization');
      console.error('Optimization error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (risk: number) => {
    if (risk < 0.05) return '#10B981';
    if (risk < 0.10) return '#F59E0B';
    return '#EF4444';
  };

  const getReturnColor = (returnValue: number) => {
    if (returnValue > 0.15) return '#10B981';
    if (returnValue > 0.10) return '#F59E0B';
    return '#EF4444';
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Quantum Portfolio Optimization</h2>
          <p className="text-gray-600">Advanced quantum algorithms for optimal portfolio allocation</p>
        </div>
        <button
          onClick={handleOptimizationRequest}
          disabled={loading}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center space-x-2"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Optimizing...</span>
            </>
          ) : (
            <>
              <span>⚛️</span>
              <span>Run Optimization</span>
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
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Algorithm</label>
            <select
              value={selectedAlgorithm}
              onChange={(e) => setSelectedAlgorithm(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500 w-full"
            >
              <option value="qaoa">QAOA (Quantum Approximate Optimization)</option>
              <option value="vqe">VQE (Variational Quantum Eigensolver)</option>
              <option value="hybrid">Hybrid Classical-Quantum</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Risk Tolerance</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={riskTolerance}
              onChange={(e) => setRiskTolerance(parseFloat(e.target.value))}
              className="w-full"
            />
            <div className="text-xs text-gray-500 mt-1">{riskTolerance.toFixed(1)}</div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Target Return (%)</label>
            <input
              type="number"
              min="0"
              max="50"
              step="0.1"
              value={targetReturn * 100}
              onChange={(e) => setTargetReturn(parseFloat(e.target.value) / 100)}
              className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500 w-full"
            />
          </div>
          <div className="flex items-end">
            <div className="text-sm text-gray-600">
              <div>Quantum Advantage: {optimizationResult?.quantum_advantage ? `${(optimizationResult.quantum_advantage * 100).toFixed(1)}%` : 'N/A'}</div>
              <div className="text-xs text-gray-500">
                {optimizationResult?.classical_fallback ? 'Using Classical Fallback' : 'Quantum Algorithm Active'}
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Portfolio Allocation Chart */}
      {optimizationResult && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white p-6 rounded-lg shadow-sm border"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Portfolio Allocation</h3>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={optimizationResult.portfolio_assets}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ symbol, optimized_weight }) => `${symbol}: ${(optimized_weight * 100).toFixed(1)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="optimized_weight"
                >
                  {optimizationResult.portfolio_assets.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `${(Number(value) * 100).toFixed(1)}%`} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold" style={{ color: getReturnColor(optimizationResult.expected_return) }}>
                    {(optimizationResult.expected_return * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-600">Expected Return</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold" style={{ color: getRiskColor(optimizationResult.risk_score) }}>
                    {(optimizationResult.risk_score * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-600">Risk Score</div>
                </div>
              </div>
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{optimizationResult.sharpe_ratio.toFixed(2)}</div>
                <div className="text-sm text-gray-600">Sharpe Ratio</div>
              </div>
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">{optimizationResult.execution_time.toFixed(2)}s</div>
                <div className="text-sm text-gray-600">Execution Time</div>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Portfolio Comparison Table */}
      {optimizationResult && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white p-6 rounded-lg shadow-sm border"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Portfolio Comparison</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Asset</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Current Weight</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Optimized Weight</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Expected Return</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risk Score</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {optimizationResult.portfolio_assets.map((asset, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{asset.symbol}</div>
                        <div className="text-sm text-gray-500">{asset.name}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {(asset.current_weight * 100).toFixed(1)}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {(asset.optimized_weight * 100).toFixed(1)}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {(asset.expected_return * 100).toFixed(1)}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {(asset.risk_score * 100).toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      )}

      {/* Risk Assessment */}
      {riskAssessment && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white p-6 rounded-lg shadow-sm border"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Assessment</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={[
              { name: 'Market', value: riskAssessment.market_risk, color: getRiskColor(riskAssessment.market_risk) },
              { name: 'Credit', value: riskAssessment.credit_risk, color: getRiskColor(riskAssessment.credit_risk) },
              { name: 'Liquidity', value: riskAssessment.liquidity_risk, color: getRiskColor(riskAssessment.liquidity_risk) },
              { name: 'Operational', value: riskAssessment.operational_risk, color: getRiskColor(riskAssessment.operational_risk) },
              { name: 'Quantum', value: riskAssessment.quantum_risk, color: getRiskColor(riskAssessment.quantum_risk) },
              { name: 'Overall', value: riskAssessment.overall_risk, color: getRiskColor(riskAssessment.overall_risk) },
            ]}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip formatter={(value) => `${(Number(value) * 100).toFixed(1)}%`} />
              <Bar dataKey="value" fill="#8884d8">
                {[
                  { name: 'Market', value: riskAssessment.market_risk, color: getRiskColor(riskAssessment.market_risk) },
                  { name: 'Credit', value: riskAssessment.credit_risk, color: getRiskColor(riskAssessment.credit_risk) },
                  { name: 'Liquidity', value: riskAssessment.liquidity_risk, color: getRiskColor(riskAssessment.liquidity_risk) },
                  { name: 'Operational', value: riskAssessment.operational_risk, color: getRiskColor(riskAssessment.operational_risk) },
                  { name: 'Quantum', value: riskAssessment.quantum_risk, color: getRiskColor(riskAssessment.quantum_risk) },
                  { name: 'Overall', value: riskAssessment.overall_risk, color: getRiskColor(riskAssessment.overall_risk) },
                ].map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      )}
    </div>
  );
};

export default QuantumOptimization;
