import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiService from '../services/api';

interface Recommendation {
  id: string;
  type: string;
  description: string;
  impact: string;
}

interface Stats {
  totalSavings: number;
  riskReduction: number;
  efficiencyGain: number;
}

const Optimization: React.FC = () => {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');
  const [executing, setExecuting] = useState<{[key: string]: boolean}>({});
  const [stats, setStats] = useState<Stats>({
    totalSavings: 0,
    riskReduction: 0,
    efficiencyGain: 0
  });
  const navigate = useNavigate();

  useEffect(() => {
    fetchOptimizationData();
  }, []);

  const fetchOptimizationData = async () => {
    try {
      setLoading(true);
      // Mock data - replace with actual API calls
      setRecommendations([
        {
          id: '1',
          type: 'Portfolio Optimization',
          description: 'Rebalance portfolio to reduce risk by 15%',
          impact: 'High'
        },
        {
          id: '2',
          type: 'Risk Management',
          description: 'Implement stop-loss orders for volatile positions',
          impact: 'Medium'
        }
      ]);
      setStats({
        totalSavings: 250000,
        riskReduction: 15,
        efficiencyGain: 12
      });
    } catch (err) {
      setError('Failed to fetch optimization data');
    } finally {
      setLoading(false);
    }
  };

  const executeRecommendation = async (id: string) => {
    setExecuting(prev => ({ ...prev, [id]: true }));
    try {
      // Mock execution
      await new Promise(resolve => setTimeout(resolve, 2000));
      setRecommendations(prev => prev.filter(rec => rec.id !== id));
    } catch (err) {
      setError('Failed to execute recommendation');
    } finally {
      setExecuting(prev => ({ ...prev, [id]: false }));
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Portfolio Optimization</h1>
          <p className="mt-2 text-gray-600">AI-powered recommendations to maximize returns and minimize risk</p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900">Total Savings</h3>
            <p className="text-3xl font-bold text-green-600">${stats.totalSavings.toLocaleString()}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900">Risk Reduction</h3>
            <p className="text-3xl font-bold text-blue-600">{stats.riskReduction}%</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900">Efficiency Gain</h3>
            <p className="text-3xl font-bold text-purple-600">{stats.efficiencyGain}%</p>
          </div>
        </div>

        {/* Recommendations */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">AI Recommendations</h2>
          </div>
          <div className="p-6">
            {recommendations.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No recommendations available</p>
            ) : (
              <div className="space-y-4">
                {recommendations.map((rec) => (
                  <div key={rec.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="text-lg font-medium text-gray-900">{rec.type}</h3>
                        <p className="text-gray-600 mt-1">{rec.description}</p>
                        <span className={`inline-block px-2 py-1 text-xs font-medium rounded-full mt-2 ${
                          rec.impact === 'High' ? 'bg-red-100 text-red-800' :
                          rec.impact === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {rec.impact} Impact
                        </span>
                      </div>
                      <button
                        onClick={() => executeRecommendation(rec.id)}
                        disabled={executing[rec.id]}
                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {executing[rec.id] ? 'Executing...' : 'Execute'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Optimization;
