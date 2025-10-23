import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiService from '../services/api';

const Optimization = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [executing, setExecuting] = useState({});
  const [stats, setStats] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    fetchOptimizationData();
  }, []);

  const fetchOptimizationData = async () => {
    try {
      setLoading(true);
      const [recs, history] = await Promise.all([
        apiService.request('/api/energy-data/optimize/recommendations'),
        apiService.request('/api/energy-data/optimize/history')
      ]);

      setRecommendations(recs.recommendations || []);
      setStats(history.statistics || {});
    } catch (err) {
      setError('Failed to fetch optimization data');
      console.error('Optimization data fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const executeRecommendation = async (recommendationId) => {
    try {
      setExecuting(prev => ({ ...prev, [recommendationId]: true }));
      
      const result = await apiService.request(
        `/api/energy-data/optimize/execute/${recommendationId}`,
        { method: 'POST' }
      );

      if (result.execution_result) {
        // Update the recommendation status
        setRecommendations(prev => 
          prev.map(rec => 
            rec.id === recommendationId 
              ? { ...rec, status: 'executed', execution_result: result.execution_result }
              : rec
          )
        );
        
        // Refresh stats
        const history = await apiService.request('/api/energy-data/optimize/history');
        setStats(history.statistics || {});
      }
    } catch (err) {
      setError(`Failed to execute recommendation: ${err.message}`);
    } finally {
      setExecuting(prev => ({ ...prev, [recommendationId]: false }));
    }
  };

  const getPriorityColor = (priority) => {
    if (priority >= 8) return 'bg-red-100 text-red-800';
    if (priority >= 6) return 'bg-orange-100 text-orange-800';
    if (priority >= 4) return 'bg-yellow-100 text-yellow-800';
    return 'bg-green-100 text-green-800';
  };

  const getConfidenceColor = (confidence) => {
    if (confidence === 'high') return 'bg-green-100 text-green-800';
    if (confidence === 'medium') return 'bg-yellow-100 text-yellow-800';
    return 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading optimization data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-lg mb-4">{error}</div>
          <button
            onClick={fetchOptimizationData}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">
                Optimization Engine
              </h1>
              <span className="ml-4 px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded-full">
                AI-Powered
              </span>
            </div>
            <button
              onClick={() => navigate('/dashboard')}
              className="bg-gray-600 text-white px-4 py-2 rounded text-sm hover:bg-gray-700"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          
          {/* Statistics Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                      <span className="text-white font-bold">T</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Total Recommendations
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {stats.total || 0}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                      <span className="text-white font-bold">E</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Executed
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {stats.executed || 0}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
                      <span className="text-white font-bold">P</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Pending
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {stats.pending || 0}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                      <span className="text-white font-bold">R</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Execution Rate
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {stats.execution_rate || 0}%
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Recommendations List */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">
                AI-Generated Recommendations
              </h2>
              <p className="mt-1 text-sm text-gray-500">
                Personalized optimization suggestions based on market conditions
              </p>
            </div>

            <div className="divide-y divide-gray-200">
              {recommendations.length === 0 ? (
                <div className="px-6 py-12 text-center">
                  <div className="text-gray-400 text-lg mb-2">No recommendations available</div>
                  <div className="text-gray-500 text-sm">
                    The AI engine is analyzing market conditions to generate personalized recommendations.
                  </div>
                </div>
              ) : (
                recommendations.map((recommendation) => (
                  <div key={recommendation.id} className="px-6 py-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="text-lg font-medium text-gray-900">
                            {recommendation.title}
                          </h3>
                          <span className={`px-2 py-1 text-xs rounded-full ${getPriorityColor(recommendation.priority)}`}>
                            Priority {recommendation.priority}
                          </span>
                          <span className={`px-2 py-1 text-xs rounded-full ${getConfidenceColor(recommendation.confidence)}`}>
                            {recommendation.confidence} confidence
                          </span>
                        </div>
                        
                        <p className="text-gray-600 mb-3">{recommendation.description}</p>
                        
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                          <div>
                            <span className="text-sm font-medium text-gray-500">Potential Savings:</span>
                            <div className="text-lg font-semibold text-green-600">
                              {recommendation.potential_savings}
                            </div>
                          </div>
                          
                          <div>
                            <span className="text-sm font-medium text-gray-500">Financial Impact:</span>
                            <div className="text-sm text-gray-900 capitalize">
                              {recommendation.estimated_impact?.financial_impact || 'N/A'}
                            </div>
                          </div>
                          
                          <div>
                            <span className="text-sm font-medium text-gray-500">Time to Implement:</span>
                            <div className="text-sm text-gray-900">
                              {recommendation.estimated_impact?.time_to_implement || 'N/A'}
                            </div>
                          </div>
                        </div>

                        {/* Implementation Steps */}
                        {recommendation.implementation_steps && (
                          <div className="mb-4">
                            <span className="text-sm font-medium text-gray-500">Implementation Steps:</span>
                            <ol className="mt-2 list-decimal list-inside space-y-1">
                              {recommendation.implementation_steps.map((step, index) => (
                                <li key={index} className="text-sm text-gray-600">{step}</li>
                              ))}
                            </ol>
                          </div>
                        )}

                        {/* Execution Result */}
                        {recommendation.status === 'executed' && recommendation.execution_result && (
                          <div className="bg-green-50 border border-green-200 rounded-md p-3 mb-4">
                            <div className="flex items-center">
                              <div className="flex-shrink-0">
                                <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                </svg>
                              </div>
                              <div className="ml-3">
                                <h4 className="text-sm font-medium text-green-800">Executed Successfully</h4>
                                <p className="text-sm text-green-700 mt-1">
                                  {recommendation.execution_result.message}
                                </p>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>

                      <div className="ml-6 flex-shrink-0">
                        {recommendation.status === 'pending' ? (
                          <button
                            onClick={() => executeRecommendation(recommendation.id)}
                            disabled={executing[recommendation.id]}
                            className={`px-4 py-2 rounded-md text-sm font-medium ${
                              executing[recommendation.id]
                                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                : 'bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
                            }`}
                          >
                            {executing[recommendation.id] ? 'Executing...' : 'Execute'}
                          </button>
                        ) : (
                          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                            Executed
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Refresh Button */}
          <div className="mt-6 text-center">
            <button
              onClick={fetchOptimizationData}
              className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Refresh Recommendations
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Optimization;
