import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import performanceOptimizer, { PerformanceMetrics } from '../services/performanceOptimizer';

interface PerformanceContextType {
  // Performance monitoring state
  isMonitoring: boolean;
  startMonitoring: () => void;
  stopMonitoring: () => void;
  
  // Performance data
  performanceData: PerformanceMetrics[] | null;
  cacheStats: {
    size: number;
    hitRate: number;
    memoryUsage: number;
  } | null;
  performanceSummary: {
    avgApiResponseTime: number;
    avgCacheHitRate: number;
    avgRenderTime: number;
    totalRequests: number;
  } | null;
  
  // Performance actions
  clearCache: () => void;
  updatePerformanceData: () => void;
  
  // Performance warnings
  warnings: string[];
  
  // Utility functions
  formatMemory: (bytes: number) => string;
  formatTime: (ms: number) => string;
  formatPercentage: (value: number) => string;
}

const PerformanceContext = createContext<PerformanceContextType | undefined>(undefined);

interface PerformanceProviderProps {
  children: ReactNode;
  autoStart?: boolean;
  updateInterval?: number;
}

export const PerformanceProvider: React.FC<PerformanceProviderProps> = ({
  children,
  autoStart = true,
  updateInterval = 5000
}) => {
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [performanceData, setPerformanceData] = useState<PerformanceMetrics[] | null>(null);
  const [cacheStats, setCacheStats] = useState<{
    size: number;
    hitRate: number;
    memoryUsage: number;
  } | null>(null);
  const [performanceSummary, setPerformanceSummary] = useState<{
    avgApiResponseTime: number;
    avgCacheHitRate: number;
    avgRenderTime: number;
    totalRequests: number;
  } | null>(null);
  const [warnings, setWarnings] = useState<string[]>([]);

  // Start performance monitoring
  const startMonitoring = () => {
    performanceOptimizer.startMonitoring();
    setIsMonitoring(true);
  };

  // Stop performance monitoring
  const stopMonitoring = () => {
    performanceOptimizer.stopMonitoring();
    setIsMonitoring(false);
  };

  // Clear cache
  const clearCache = () => {
    performanceOptimizer.clearCache();
    updatePerformanceData();
  };

  // Update performance data
  const updatePerformanceData = () => {
    if (isMonitoring) {
      const newPerformanceData = performanceOptimizer.getPerformanceMetrics();
      const newCacheStats = performanceOptimizer.getCacheStats();
      const newPerformanceSummary = performanceOptimizer.getPerformanceSummary();

      setPerformanceData(newPerformanceData);
      setCacheStats(newCacheStats);
      setPerformanceSummary(newPerformanceSummary);

      // Generate performance warnings
      generateWarnings(newPerformanceSummary, newCacheStats);
    }
  };

  // Generate performance warnings
  const generateWarnings = (
    summary: any,
    cache: any
  ) => {
    const newWarnings: string[] = [];

    // API response time warnings
    if (summary?.avgApiResponseTime > 1000) {
      newWarnings.push(`Slow API response time: ${summary.avgApiResponseTime.toFixed(2)}ms`);
    }

    // Cache hit rate warnings
    if (cache?.hitRate < 50) {
      newWarnings.push(`Low cache hit rate: ${cache.hitRate.toFixed(2)}%`);
    }

    // Memory usage warnings
    if (cache?.memoryUsage > 50 * 1024 * 1024) { // 50MB
      newWarnings.push(`High memory usage: ${(cache.memoryUsage / 1024 / 1024).toFixed(2)}MB`);
    }

    // Render time warnings
    if (summary?.avgRenderTime > 100) {
      newWarnings.push(`Slow render time: ${summary.avgRenderTime.toFixed(2)}ms`);
    }

    setWarnings(newWarnings);
  };

  // Utility functions
  const formatMemory = (bytes: number): string => {
    if (bytes < 1024) return `${bytes}B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)}KB`;
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(2)}MB`;
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)}GB`;
  };

  const formatTime = (ms: number): string => {
    if (ms < 1000) return `${ms.toFixed(2)}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(2)}s`;
    return `${(ms / 60000).toFixed(2)}m`;
  };

  const formatPercentage = (value: number): string => {
    return `${(value * 100).toFixed(2)}%`;
  };

  // Auto-start monitoring
  useEffect(() => {
    if (autoStart) {
      startMonitoring();
    }
  }, [autoStart]);

  // Periodic performance updates
  useEffect(() => {
    if (isMonitoring) {
      const interval = setInterval(updatePerformanceData, updateInterval);
      return () => clearInterval(interval);
    }
  }, [isMonitoring, updateInterval]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (isMonitoring) {
        stopMonitoring();
      }
    };
  }, [isMonitoring]);

  const value: PerformanceContextType = {
    isMonitoring,
    startMonitoring,
    stopMonitoring,
    performanceData,
    cacheStats,
    performanceSummary,
    clearCache,
    updatePerformanceData,
    warnings,
    formatMemory,
    formatTime,
    formatPercentage
  };

  return (
    <PerformanceContext.Provider value={value}>
      {children}
    </PerformanceContext.Provider>
  );
};

// Custom hook to use performance context
export const usePerformance = (): PerformanceContextType => {
  const context = useContext(PerformanceContext);
  if (context === undefined) {
    throw new Error('usePerformance must be used within a PerformanceProvider');
  }
  return context;
};

export default PerformanceContext;
