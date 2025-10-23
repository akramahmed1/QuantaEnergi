import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
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
  Atom, 
  Zap, 
  Brain, 
  Target,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertTriangle,
  Cpu,
  Database,
  Activity,
  BarChart3,
  PieChart,
  Settings,
  Play,
  Pause,
  RotateCcw
} from 'lucide-react';

interface QuantumOptimizationDashboardProps {
  userId?: string;
}

const QuantumOptimizationDashboard: React.FC<QuantumOptimizationDashboardProps> = ({ userId = 'user123' }) => {
  const [selectedMethod, setSelectedMethod] = useState('quantum_qaoa');
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [optimizationResult, setOptimizationResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Sample optimization methods
  const methods = [
    { 
      id: 'quantum_qaoa', 
      name: 'Quantum QAOA', 
      description: 'Quantum Approximate Optimization Algorithm',
      advantage: true,
      sharpe: 1.92,
      time: 0.8,
      accuracy: 95,
      color: '#8884d8'
    },
    { 
      id: 'classical_pulp', 
      name: 'Classical PuLP', 
      description: 'Linear Programming Optimization',
      advantage: false,
      sharpe: 1.85,
      time: 2.1,
      accuracy: 98,
      color: '#82ca9d'
    },
    { 
      id: 'numpy_fallback', 
      name: 'NumPy Fallback', 
      description: 'Analytical Solution Method',
      advantage: false,
      sharpe: 1.78,
      time: 0.3,
      accuracy: 92,
      color: '#ffc658'
    }
  ];

  const portfolioData = [
    { asset: 'Crude Oil', weight: 0.35, return: 0.12, risk: 0.18, sharpe: 0.67 },
    { asset: 'Natural Gas', weight: 0.25, return: 0.08, risk: 0.22, sharpe: 0.36 },
    { asset: 'Refined Products', weight: 0.20, return: 0.15, risk: 0.15, sharpe: 1.00 },
    { asset: 'Renewables', weight: 0.20, return: 0.10, risk: 0.12, sharpe: 0.83 }
  ];

  const optimizationHistory = [
    { iteration: 1, quantum: 1.65, classical: 1.60, numpy: 1.55 },
    { iteration: 2, quantum: 1.72, classical: 1.68, numpy: 1.62 },
    { iteration: 3, quantum: 1.78, classical: 1.75, numpy: 1.70 },
    { iteration: 4, quantum: 1.82, classical: 1.80, numpy: 1.75 },
    { iteration: 5, quantum: 1.85, classical: 1.83, numpy: 1.78 },
    { iteration: 6, quantum: 1.88, classical: 1.85, numpy: 1.80 },
    { iteration: 7, quantum: 1.90, classical: 1.87, numpy: 1.82 },
    { iteration: 8, quantum: 1.92, classical: 1.88, numpy: 1.85 }
  ];

  const quantumMetrics = [
    { metric: 'Qubits Used', value: 12, max: 20, unit: 'qubits' },
    { metric: 'Circuit Depth', value: 45, max: 100, unit: 'gates' },
    { metric: 'Entanglement', value: 0.78, max: 1.0, unit: 'ratio' },
    { metric: 'Coherence Time', value: 150, max: 200, unit: 'μs' }
  ];

  const performanceComparison = [
    { method: 'Quantum QAOA', sharpe: 1.92, time: 0.8, accuracy: 95, advantage: true },
    { method: 'Classical PuLP', sharpe: 1.85, time: 2.1, accuracy: 98, advantage: false },
    { method: 'NumPy Fallback', sharpe: 1.78, time: 0.3, accuracy: 92, advantage: false }
  ];

  const quantumAdvantage = [
    { portfolio_size: 5, quantum_time: 0.5, classical_time: 1.2, advantage: 2.4 },
    { portfolio_size: 10, quantum_time: 0.8, classical_time: 2.1, advantage: 2.6 },
    { portfolio_size: 20, quantum_time: 1.2, classical_time: 4.5, advantage: 3.8 },
    { portfolio_size: 50, quantum_time: 2.1, classical_time: 12.3, advantage: 5.9 },
    { portfolio_size: 100, quantum_time: 3.8, classical_time: 28.7, advantage: 7.6 }
  ];

  const selectedMethodData = methods.find(m => m.id === selectedMethod);

  const handleOptimize = async () => {
    setIsOptimizing(true);
    setError(null);
    
    try {
      // Simulate optimization process
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const result = {
        method: selectedMethod,
        weights: [0.35, 0.25, 0.20, 0.20],
        expectedReturn: 0.115,
        risk: 0.16,
        sharpeRatio: selectedMethodData?.sharpe || 1.85,
        optimizationTime: selectedMethodData?.time || 2.1,
        quantumAdvantage: selectedMethodData?.advantage || false
      };
      
      setOptimizationResult(result);
    } catch (err) {
      setError('Optimization failed. Please try again.');
    } finally {
      setIsOptimizing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Atom className="h-8 w-8 text-purple-600" />
              <h1 className="ml-3 text-2xl font-bold text-gray-900">Quantum Optimization Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600">
                Quantum-Enhanced Portfolio Optimization
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Method Selector */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-4 py-4">
            {methods.map((method) => (
              <button
                key={method.id}
                onClick={() => setSelectedMethod(method.id)}
                className={`flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedMethod === method.id
                    ? 'bg-purple-100 text-purple-700'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                <Atom className="h-4 w-4 mr-2" />
                {method.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* Optimization Controls */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Portfolio Optimization</h3>
              <div className="flex items-center space-x-4">
                <button
                  onClick={handleOptimize}
                  disabled={isOptimizing}
                  className={`flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isOptimizing
                      ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                      : 'bg-purple-600 text-white hover:bg-purple-700'
                  }`}
                >
                  {isOptimizing ? (
                    <>
                      <RotateCcw className="h-4 w-4 mr-2 animate-spin" />
                      Optimizing...
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 mr-2" />
                      Optimize Portfolio
                    </>
                  )}
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {selectedMethodData?.sharpe.toFixed(2)}
                </div>
                <div className="text-sm text-gray-600">Expected Sharpe Ratio</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {selectedMethodData?.time}s
                </div>
                <div className="text-sm text-gray-600">Optimization Time</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {selectedMethodData?.accuracy}%
                </div>
                <div className="text-sm text-gray-600">Accuracy</div>
              </div>
            </div>
          </div>

          {/* Optimization Results */}
          {optimizationResult && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Optimization Results</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">
                    {optimizationResult.sharpeRatio.toFixed(3)}
                  </div>
                  <div className="text-sm text-gray-600">Sharpe Ratio</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">
                    {(optimizationResult.expectedReturn * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-600">Expected Return</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">
                    {(optimizationResult.risk * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-600">Risk</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">
                    {optimizationResult.optimizationTime}s
                  </div>
                  <div className="text-sm text-gray-600">Time</div>
                </div>
              </div>
            </div>
          )}

          {/* Portfolio Allocation */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Portfolio Allocation</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={portfolioData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="asset" />
                <YAxis />
                <Tooltip formatter={(value, name) => [
                  name === 'weight' ? `${(value as number * 100).toFixed(1)}%` : value,
                  name === 'weight' ? 'Weight' : name
                ]} />
                <Legend />
                <Bar dataKey="weight" fill="#8884d8" name="Weight" />
                <Bar dataKey="return" fill="#82ca9d" name="Return" />
                <Bar dataKey="risk" fill="#ffc658" name="Risk" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Optimization Convergence */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Optimization Convergence</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={optimizationHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="iteration" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="quantum" stroke="#8884d8" strokeWidth={2} name="Quantum QAOA" />
                <Line type="monotone" dataKey="classical" stroke="#82ca9d" strokeWidth={2} name="Classical PuLP" />
                <Line type="monotone" dataKey="numpy" stroke="#ffc658" strokeWidth={2} name="NumPy Fallback" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Quantum Advantage Analysis */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quantum Advantage</h3>
              <ResponsiveContainer width="100%" height={250}>
                <ComposedChart data={quantumAdvantage}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="portfolio_size" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Legend />
                  <Bar yAxisId="left" dataKey="quantum_time" fill="#8884d8" name="Quantum Time (s)" />
                  <Bar yAxisId="left" dataKey="classical_time" fill="#82ca9d" name="Classical Time (s)" />
                  <Line yAxisId="right" type="monotone" dataKey="advantage" stroke="#ff7300" strokeWidth={2} name="Advantage (x)" />
                </ComposedChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Method Comparison</h3>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={performanceComparison}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="method" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="sharpe" fill="#8884d8" name="Sharpe Ratio" />
                  <Bar dataKey="time" fill="#82ca9d" name="Time (s)" />
                  <Bar dataKey="accuracy" fill="#ffc658" name="Accuracy (%)" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Quantum Metrics */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quantum System Metrics</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {quantumMetrics.map((metric, index) => (
                <div key={index} className="text-center">
                  <div className="text-2xl font-bold text-gray-900">
                    {metric.value}{metric.unit === 'ratio' ? '' : metric.unit}
                  </div>
                  <div className="text-sm text-gray-600">{metric.metric}</div>
                  <div className="mt-2">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-purple-600 h-2 rounded-full" 
                        style={{ width: `${(metric.value / metric.max) * 100}%` }}
                      ></div>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {Math.round((metric.value / metric.max) * 100)}% of max
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quantum Status */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quantum System Status</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center">
                  <Atom className="h-6 w-6 text-purple-600 mr-3" />
                  <div>
                    <p className="font-medium">Qiskit Available</p>
                    <p className="text-sm text-gray-600">Quantum SDK</p>
                  </div>
                </div>
                <CheckCircle className="h-5 w-5 text-green-500" />
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center">
                  <Cpu className="h-6 w-6 text-blue-600 mr-3" />
                  <div>
                    <p className="font-medium">Quantum Hardware</p>
                    <p className="text-sm text-gray-600">IBM Quantum</p>
                  </div>
                </div>
                <Clock className="h-5 w-5 text-yellow-500" />
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center">
                  <Database className="h-6 w-6 text-green-600 mr-3" />
                  <div>
                    <p className="font-medium">Classical Fallback</p>
                    <p className="text-sm text-gray-600">PuLP Available</p>
                  </div>
                </div>
                <CheckCircle className="h-5 w-5 text-green-500" />
              </div>
            </div>
          </div>

          {/* Recommendations */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Optimization Recommendations</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[
                { 
                  title: 'Use Quantum QAOA', 
                  description: 'For portfolios with 20+ assets, quantum advantage becomes significant',
                  priority: 'High',
                  icon: Atom
                },
                { 
                  title: 'Classical Fallback', 
                  description: 'Use PuLP for smaller portfolios or when quantum hardware unavailable',
                  priority: 'Medium',
                  icon: Cpu
                },
                { 
                  title: 'Hybrid Approach', 
                  description: 'Combine quantum and classical methods for optimal results',
                  priority: 'High',
                  icon: Brain
                },
                { 
                  title: 'Real-time Optimization', 
                  description: 'Implement continuous portfolio rebalancing using quantum algorithms',
                  priority: 'Medium',
                  icon: Activity
                },
                { 
                  title: 'Risk-Adjusted Returns', 
                  description: 'Focus on Sharpe ratio optimization for better risk-adjusted performance',
                  priority: 'Critical',
                  icon: Target
                },
                { 
                  title: 'Quantum Advantage', 
                  description: 'Leverage quantum advantage for complex multi-objective optimization',
                  priority: 'High',
                  icon: Zap
                }
              ].map((recommendation, index) => {
                const Icon = recommendation.icon;
                return (
                  <div key={index} className="p-4 border rounded-lg">
                    <div className="flex items-start">
                      <Icon className="h-6 w-6 text-purple-600 mt-1 mr-3" />
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

export default QuantumOptimizationDashboard;
