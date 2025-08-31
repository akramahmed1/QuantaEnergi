import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import apiService from '../services/api';

const TradingDashboard = () => {
  const [user, setUser] = useState(null);
  const [showErrorModal, setShowErrorModal] = useState(false);
  const [errorDetails, setErrorDetails] = useState('');
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  useEffect(() => {
    const currentUser = apiService.getCurrentUserData();
    if (!currentUser) {
      navigate('/login');
      return;
    }
    setUser(currentUser);
  }, [navigate]);

  // React Query hooks for data fetching
  const { data: marketData, isLoading: marketLoading, error: marketError } = useQuery(
    'marketPrices',
    apiService.getMarketPrices,
    {
      retry: 3,
      retryDelay: 1000,
      onError: (error) => {
        setErrorDetails(error.message || 'Failed to fetch market data');
        setShowErrorModal(true);
      }
    }
  );

  const { data: renewableData, isLoading: renewableLoading, error: renewableError } = useQuery(
    'renewableEnergy',
    apiService.getRenewableEnergy,
    {
      retry: 3,
      retryDelay: 1000,
      onError: (error) => {
        setErrorDetails(error.message || 'Failed to fetch renewable data');
        setShowErrorModal(true);
      }
    }
  );

  // Enhanced React Query with better retry logic and caching
  const { data: forecastData, isLoading: forecastLoading, error: forecastError } = useQuery(
    'energyForecast',
    () => apiService.getEnergyForecast('crude_oil', 30),
    {
      retry: (failureCount, error) => {
        // Retry up to 3 times, but not for 4xx errors
        if (failureCount < 3 && error?.response?.status >= 500) {
          return true;
        }
        return false;
      },
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      onError: (error) => {
        setErrorDetails(error.message || 'Failed to fetch forecast data');
        setShowErrorModal(true);
      }
    }
  );

  const { data: analyticsData, isLoading: analyticsLoading, error: analyticsError } = useQuery(
    'userAnalytics',
    apiService.getUserAnalytics,
    {
      retry: 3,
      retryDelay: 1000,
      staleTime: 2 * 60 * 1000, // 2 minutes for analytics
      onError: (error) => {
        setErrorDetails(error.message || 'Failed to fetch analytics data');
        setShowErrorModal(true);
      }
    }
  );

  const isLoading = marketLoading || renewableLoading || forecastLoading || analyticsLoading;
  const hasError = marketError || renewableError || forecastError || analyticsError;

  // WebSocket connection for real-time updates
  useEffect(() => {
    let ws = null;
    
    const connectWebSocket = () => {
      try {
        ws = new WebSocket('ws://localhost:8000/ws/market');
        
        ws.onopen = () => {
          console.log('WebSocket connected for market updates');
        };
        
        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'market_update') {
              // Invalidate and refetch market data
              queryClient.invalidateQueries(['marketPrices']);
              console.log('Real-time market update received:', data);
            }
          } catch (err) {
            console.error('WebSocket message parse error:', err);
          }
        };
        
        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
        };
        
        ws.onclose = () => {
          console.log('WebSocket disconnected, attempting to reconnect...');
          setTimeout(connectWebSocket, 5000);
        };
        
      } catch (err) {
        console.error('WebSocket connection error:', err);
      }
    };
    
    connectWebSocket();
    
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [queryClient]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [prices, renewables] = await Promise.all([
        apiService.getMarketPrices(),
        apiService.getRenewableEnergy()
      ]);
      
      setMarketData(prices);
      setRenewableData(renewables);
    } catch (err) {
      setError('Failed to fetch dashboard data');
      console.error('Dashboard data fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    apiService.logout();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
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
            onClick={fetchDashboardData}
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
                EnergyOpti-Pro Trading Platform
              </h1>
              <span className="ml-4 px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                {user?.role || 'User'}
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600">
                Welcome, {user?.company_name || user?.email}
              </div>
              <button
                onClick={() => navigate('/optimization')}
                className="bg-purple-600 text-white px-3 py-2 rounded text-sm hover:bg-purple-700"
              >
                Optimization
              </button>
              <button
                onClick={handleLogout}
                className="bg-red-600 text-white px-2 py-2 rounded text-sm hover:bg-red-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          
          {/* Market Overview Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            
            {/* Market Prices Card */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                      <span className="text-white font-bold">M</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Market Prices
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {marketData ? (
                          <>
                            WTI: ${marketData.cme_crude?.data || 'N/A'} | 
                            Brent: ${marketData.ice_brent?.data || 'N/A'}
                          </>
                        ) : (
                          'Loading...'
                        )}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            {/* Portfolio Value Card */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                      <span className="text-white font-bold">P</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Portfolio Value
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        $1,250,000
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            {/* AI Insights Card */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                      <span className="text-white font-bold">AI</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        AI Insights
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        Price Breakout Expected
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            {/* Renewable Energy Card */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
                      <span className="text-white font-bold">R</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Renewable Energy
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {renewableData ? (
                          <>
                            Wind: {renewableData.wind}MW | 
                            Solar: {renewableData.solar}MW
                          </>
                        ) : (
                          'Loading...'
                        )}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            {/* ESG Score Card */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-teal-500 rounded-md flex items-center justify-center">
                      <span className="text-white font-bold">E</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        ESG Score
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        78/100
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            {/* Risk Level Card */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-red-500 rounded-md flex items-center justify-center">
                      <span className="text-white font-bold">R</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Risk Level
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        Medium
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

          </div>

          {/* API Status */}
          <div className="bg-white shadow rounded-lg p-6 mb-8">
            <h2 className="text-lg font-medium text-gray-900 mb-4">API Status</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-md">
                <span className="text-sm font-medium text-green-800">Backend API</span>
                <span className="text-sm text-green-600">✅ Healthy</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-md">
                <span className="text-sm font-medium text-green-800">Authentication</span>
                <span className="text-sm text-green-600">✅ Active</span>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white shadow rounded-lg p-6 mb-8">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button 
                onClick={() => window.open('http://localhost:8000/docs', '_blank')}
                className="block p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-left"
              >
                <h3 className="font-medium text-gray-900">API Documentation</h3>
                <p className="text-sm text-gray-500">Swagger UI</p>
              </button>
              <button 
                onClick={() => window.open('http://localhost:8000/api/health', '_blank')}
                className="block p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-left"
              >
                <h3 className="font-medium text-gray-900">Health Check</h3>
                <p className="text-sm text-gray-500">API Status</p>
              </button>
              <button 
                onClick={() => window.open('http://localhost:8000/api/prices', '_blank')}
                className="block p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-left"
              >
                <h3 className="font-medium text-gray-900">Market Prices</h3>
                <p className="text-sm text-gray-500">Live Data</p>
              </button>
            </div>
          </div>

          {/* User Info */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">User Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Email</p>
                <p className="text-sm font-medium text-gray-900">{user?.email}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Company</p>
                <p className="text-sm font-medium text-gray-900">{user?.company_name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Role</p>
                <p className="text-sm font-medium text-gray-900">{user?.role}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">User ID</p>
                <p className="text-sm font-medium text-gray-900">{user?.id}</p>
              </div>
            </div>
          </div>

        </div>
      </main>

      {/* Error Modal */}
      {showErrorModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex items-center mb-4">
              <div className="text-red-600 text-2xl mr-3">⚠️</div>
              <h3 className="text-lg font-semibold text-gray-900">Error</h3>
            </div>
            <p className="text-gray-600 mb-6">{errorDetails}</p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowErrorModal(false)}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded hover:bg-gray-50"
              >
                Close
              </button>
              <button
                onClick={() => {
                  queryClient.invalidateQueries(['marketPrices', 'renewableEnergy']);
                  setShowErrorModal(false);
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TradingDashboard;
