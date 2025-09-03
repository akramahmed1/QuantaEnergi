import React, { useState, useEffect, useRef } from 'react';
import performanceOptimizer, { CacheConfig, BatchConfig } from '../services/performanceOptimizer';

interface PerformanceMonitoringDashboardProps {
  userId?: string;
}

const PerformanceMonitoringDashboard: React.FC<PerformanceMonitoringDashboardProps> = ({ userId = 'user123' }) => {
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'cache' | 'batching' | 'metrics'>('overview');
  const [cacheConfig, setCacheConfig] = useState<CacheConfig>({
    maxSize: 1000,
    ttl: 5 * 60 * 1000,
    enableCompression: true
  });
  const [batchConfig, setBatchConfig] = useState<BatchConfig>({
    maxBatchSize: 10,
    maxWaitTime: 100,
    enableRetry: true,
    maxRetries: 3
  });
  const [performanceData, setPerformanceData] = useState<any>(null);
  const [cacheStats, setCacheStats] = useState<any>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Start/stop monitoring
  const toggleMonitoring = () => {
    if (isMonitoring) {
      performanceOptimizer.stopMonitoring();
      setIsMonitoring(false);
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    } else {
      performanceOptimizer.startMonitoring();
      setIsMonitoring(true);
      // Update data every 2 seconds
      intervalRef.current = setInterval(updatePerformanceData, 2000);
    }
  };

  // Update performance data
  const updatePerformanceData = () => {
    if (isMonitoring) {
      setPerformanceData(performanceOptimizer.getPerformanceSummary());
      setCacheStats(performanceOptimizer.getCacheStats());
    }
  };

  // Update cache configuration
  const updateCacheConfig = (newConfig: Partial<CacheConfig>) => {
    const updatedConfig = { ...cacheConfig, ...newConfig };
    setCacheConfig(updatedConfig);
    performanceOptimizer.setCacheConfig(updatedConfig);
  };

  // Update batch configuration
  const updateBatchConfig = (newConfig: Partial<BatchConfig>) => {
    const updatedConfig = { ...batchConfig, ...newConfig };
    setBatchConfig(updatedConfig);
    performanceOptimizer.setBatchConfig(updatedConfig);
  };

  // Clear cache
  const clearCache = () => {
    performanceOptimizer.clearCache();
    updatePerformanceData();
  };

  // Format time in milliseconds
  const formatTime = (ms: number): string => {
    if (ms < 1000) return `${ms.toFixed(2)}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(2)}s`;
    return `${(ms / 60000).toFixed(2)}m`;
  };

  // Format memory usage
  const formatMemory = (bytes: number): string => {
    if (bytes < 1024) return `${bytes}B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)}KB`;
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(2)}MB`;
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)}GB`;
  };

  // Format percentage
  const formatPercentage = (value: number): string => {
    return `${(value * 100).toFixed(2)}%`;
  };

  useEffect(() => {
    // Initialize with current settings
    setCacheConfig({
      maxSize: 1000,
      ttl: 5 * 60 * 1000,
      enableCompression: true
    });
    setBatchConfig({
      maxBatchSize: 10,
      maxWaitTime: 100,
      enableRetry: true,
      maxRetries: 3
    });

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Performance Monitoring Dashboard</h1>
            <p className="text-gray-600">Monitor and optimize platform performance in real-time</p>
          </div>
          <button
            onClick={toggleMonitoring}
            className={`px-6 py-3 rounded-lg font-medium transition-colors ${
              isMonitoring
                ? 'bg-red-600 text-white hover:bg-red-700'
                : 'bg-green-600 text-white hover:bg-green-700'
            }`}
          >
            {isMonitoring ? 'Stop Monitoring' : 'Start Monitoring'}
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="mb-6">
        <nav className="flex space-x-8">
          {[
            { id: 'overview', name: 'Overview', icon: '📊' },
            { id: 'cache', name: 'Cache Management', icon: '💾' },
            { id: 'batching', name: 'Request Batching', icon: '📦' },
            { id: 'metrics', name: 'Performance Metrics', icon: '📈' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.name}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-lg shadow">
        {activeTab === 'overview' && (
          <div className="p-6">
            <h2 className="text-xl font-semibold mb-6">Performance Overview</h2>
            
            {/* Status Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <span className="text-2xl">📊</span>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-blue-600">Monitoring Status</p>
                    <p className="text-lg font-semibold text-blue-900">
                      {isMonitoring ? 'Active' : 'Inactive'}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-green-50 rounded-lg p-4">
                <div className="flex items-center">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <span className="text-2xl">⚡</span>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-green-600">Avg Response Time</p>
                    <p className="text-lg font-semibold text-green-900">
                      {performanceData ? formatTime(performanceData.avgApiResponseTime) : 'N/A'}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-purple-50 rounded-lg p-4">
                <div className="flex items-center">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <span className="text-2xl">💾</span>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-purple-600">Cache Hit Rate</p>
                    <p className="text-lg font-semibold text-purple-900">
                      {performanceData ? formatPercentage(performanceData.avgCacheHitRate) : 'N/A'}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-orange-50 rounded-lg p-4">
                <div className="flex items-center">
                  <div className="p-2 bg-orange-100 rounded-lg">
                    <span className="text-2xl">🎯</span>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-orange-600">Total Requests</p>
                    <p className="text-lg font-semibold text-orange-900">
                      {performanceData ? performanceData.totalRequests.toLocaleString() : '0'}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Performance Chart Placeholder */}
            <div className="bg-gray-50 rounded-lg p-8 text-center">
              <span className="text-4xl mb-4 block">📈</span>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Performance Trends</h3>
              <p className="text-gray-600">Real-time performance metrics visualization</p>
              <p className="text-sm text-gray-500 mt-2">
                {isMonitoring ? 'Collecting data...' : 'Start monitoring to see performance trends'}
              </p>
            </div>
          </div>
        )}

        {activeTab === 'cache' && (
          <div className="p-6">
            <h2 className="text-xl font-semibold mb-6">Cache Management</h2>
            
            {/* Cache Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-blue-50 rounded-lg p-4">
                <h3 className="font-medium text-blue-900 mb-2">Cache Size</h3>
                <p className="text-2xl font-bold text-blue-600">
                  {cacheStats ? cacheStats.size.toLocaleString() : '0'}
                </p>
                <p className="text-sm text-blue-600">entries</p>
              </div>

              <div className="bg-green-50 rounded-lg p-4">
                <h3 className="font-medium text-green-900 mb-2">Hit Rate</h3>
                <p className="text-2xl font-bold text-green-600">
                  {cacheStats ? formatPercentage(cacheStats.hitRate / 100) : '0%'}
                </p>
                <p className="text-sm text-green-600">cache efficiency</p>
              </div>

              <div className="bg-purple-50 rounded-lg p-4">
                <h3 className="font-medium text-purple-900 mb-2">Memory Usage</h3>
                <p className="text-2xl font-bold text-purple-600">
                  {cacheStats ? formatMemory(cacheStats.memoryUsage) : '0B'}
                </p>
                <p className="text-sm text-purple-600">heap memory</p>
              </div>
            </div>

            {/* Cache Configuration */}
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium mb-4">Cache Configuration</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Max Cache Size
                    </label>
                    <input
                      type="number"
                      value={cacheConfig.maxSize}
                      onChange={(e) => updateCacheConfig({ maxSize: parseInt(e.target.value) })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      TTL (minutes)
                    </label>
                    <input
                      type="number"
                      value={Math.round(cacheConfig.ttl / 60000)}
                      onChange={(e) => updateCacheConfig({ ttl: parseInt(e.target.value) * 60000 })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="enableCompression"
                      checked={cacheConfig.enableCompression}
                      onChange={(e) => updateCacheConfig({ enableCompression: e.target.checked })}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="enableCompression" className="ml-2 text-sm text-gray-700">
                      Enable Compression
                    </label>
                  </div>
                </div>
              </div>

              <div className="flex space-x-4">
                <button
                  onClick={clearCache}
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                >
                  Clear Cache
                </button>
                <button
                  onClick={() => updateCacheConfig({ maxSize: 1000, ttl: 5 * 60 * 1000, enableCompression: true })}
                  className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
                >
                  Reset to Defaults
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'batching' && (
          <div className="p-6">
            <h2 className="text-xl font-semibold mb-6">Request Batching Configuration</h2>
            
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Max Batch Size
                  </label>
                  <input
                    type="number"
                    value={batchConfig.maxBatchSize}
                    onChange={(e) => updateBatchConfig({ maxBatchSize: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <p className="text-sm text-gray-500 mt-1">Maximum requests per batch</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Max Wait Time (ms)
                  </label>
                  <input
                    type="number"
                    value={batchConfig.maxWaitTime}
                    onChange={(e) => updateBatchConfig({ maxWaitTime: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <p className="text-sm text-gray-500 mt-1">Maximum time to wait before executing batch</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Max Retries
                  </label>
                  <input
                    type="number"
                    value={batchConfig.maxRetries}
                    onChange={(e) => updateBatchConfig({ maxRetries: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <p className="text-sm text-gray-500 mt-1">Maximum retry attempts for failed batches</p>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="enableRetry"
                    checked={batchConfig.enableRetry}
                    onChange={(e) => updateBatchConfig({ enableRetry: e.target.checked })}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="enableRetry" className="ml-2 text-sm text-gray-700">
                    Enable Retry Logic
                  </label>
                </div>
              </div>

              <div className="flex space-x-4">
                <button
                  onClick={() => updateBatchConfig({ maxBatchSize: 10, maxWaitTime: 100, enableRetry: true, maxRetries: 3 })}
                  className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
                >
                  Reset to Defaults
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'metrics' && (
          <div className="p-6">
            <h2 className="text-xl font-semibold mb-6">Performance Metrics</h2>
            
            {!isMonitoring ? (
              <div className="text-center py-12">
                <span className="text-6xl block mb-4">📊</span>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Data Available</h3>
                <p className="text-gray-600">Start monitoring to collect performance metrics</p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Performance Summary */}
                <div className="bg-gray-50 rounded-lg p-6">
                  <h3 className="text-lg font-medium mb-4">Performance Summary</h3>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Average API Response Time</p>
                      <p className="text-xl font-semibold text-gray-900">
                        {performanceData ? formatTime(performanceData.avgApiResponseTime) : 'N/A'}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Average Cache Hit Rate</p>
                      <p className="text-xl font-semibold text-gray-900">
                        {performanceData ? formatPercentage(performanceData.avgCacheHitRate) : 'N/A'}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Average Render Time</p>
                      <p className="text-xl font-semibold text-gray-900">
                        {performanceData ? formatTime(performanceData.avgRenderTime) : 'N/A'}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Total Requests</p>
                      <p className="text-xl font-semibold text-gray-900">
                        {performanceData ? performanceData.totalRequests.toLocaleString() : '0'}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Real-time Metrics Chart Placeholder */}
                <div className="bg-gray-50 rounded-lg p-8 text-center">
                  <span className="text-4xl mb-4 block">📈</span>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Real-time Performance Chart</h3>
                  <p className="text-gray-600">Live performance metrics visualization</p>
                  <p className="text-sm text-gray-500 mt-2">Data updates every 2 seconds</p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default PerformanceMonitoringDashboard;
