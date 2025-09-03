/**
 * Custom React Hook for Performance Optimization
 * Provides performance monitoring, caching, and optimization features
 */

import { useEffect, useRef, useCallback, useState } from 'react';
import performanceOptimizer, { PerformanceMetrics } from '../services/performanceOptimizer';

interface UsePerformanceOptimizationOptions {
  enableMonitoring?: boolean;
  enableCaching?: boolean;
  cacheKey?: string;
  ttl?: number;
  recordRenderTime?: boolean;
}

interface PerformanceData {
  renderTime: number;
  memoryUsage: number;
  cacheStats: {
    size: number;
    hitRate: number;
    memoryUsage: number;
  };
  apiMetrics: {
    avgResponseTime: number;
    avgCacheHitRate: number;
    totalRequests: number;
  };
}

export const usePerformanceOptimization = (
  options: UsePerformanceOptimizationOptions = {}
) => {
  const {
    enableMonitoring = true,
    enableCaching = true,
    cacheKey,
    ttl,
    recordRenderTime = true
  } = options;

  const [performanceData, setPerformanceData] = useState<PerformanceData | null>(null);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const renderStartTime = useRef<number>(0);
  const componentRef = useRef<HTMLDivElement>(null);

  // Start performance monitoring
  const startMonitoring = useCallback(() => {
    if (enableMonitoring) {
      performanceOptimizer.startMonitoring();
      setIsMonitoring(true);
    }
  }, [enableMonitoring]);

  // Stop performance monitoring
  const stopMonitoring = useCallback(() => {
    if (enableMonitoring) {
      performanceOptimizer.stopMonitoring();
      setIsMonitoring(false);
    }
  }, [enableMonitoring]);

  // Record render time
  const recordRenderTime = useCallback(() => {
    if (recordRenderTime && renderStartTime.current > 0) {
      const renderTime = performance.now() - renderStartTime.current;
      performanceOptimizer.recordRenderTime(renderTime);
      
      setPerformanceData(prev => prev ? {
        ...prev,
        renderTime
      } : null);
    }
  }, [recordRenderTime]);

  // Get cached data
  const getCached = useCallback(<T>(key: string): T | null => {
    if (!enableCaching) return null;
    return performanceOptimizer.getCached<T>(key);
  }, [enableCaching]);

  // Set cached data
  const setCached = useCallback(<T>(key: string, data: T, customTtl?: number): void => {
    if (!enableCaching) return;
    performanceOptimizer.setCached(key, data, customTtl || ttl);
  }, [enableCaching, ttl]);

  // Clear cache
  const clearCache = useCallback(() => {
    if (!enableCaching) return;
    performanceOptimizer.clearCache();
  }, [enableCaching]);

  // Get cache statistics
  const getCacheStats = useCallback(() => {
    if (!enableCaching) return null;
    return performanceOptimizer.getCacheStats();
  }, [enableCaching]);

  // Get performance summary
  const getPerformanceSummary = useCallback(() => {
    if (!enableMonitoring) return null;
    return performanceOptimizer.getPerformanceSummary();
  }, [enableMonitoring]);

  // Update performance data
  const updatePerformanceData = useCallback(() => {
    if (!enableMonitoring) return;

    const cacheStats = getCacheStats();
    const apiMetrics = getPerformanceSummary();

    if (cacheStats || apiMetrics) {
      setPerformanceData({
        renderTime: 0,
        memoryUsage: cacheStats?.memoryUsage || 0,
        cacheStats: cacheStats || { size: 0, hitRate: 0, memoryUsage: 0 },
        apiMetrics: apiMetrics || { avgResponseTime: 0, avgCacheHitRate: 0, totalRequests: 0 }
      });
    }
  }, [enableMonitoring, getCacheStats, getPerformanceSummary]);

  // Debounced performance update
  const debouncedUpdate = useCallback(
    debounce(updatePerformanceData, 1000),
    [updatePerformanceData]
  );

  // Effect for starting monitoring
  useEffect(() => {
    if (enableMonitoring) {
      startMonitoring();
      return () => stopMonitoring();
    }
  }, [enableMonitoring, startMonitoring, stopMonitoring]);

  // Effect for recording render start time
  useEffect(() => {
    if (recordRenderTime) {
      renderStartTime.current = performance.now();
    }
  });

  // Effect for recording render end time
  useEffect(() => {
    if (recordRenderTime) {
      const timer = setTimeout(recordRenderTime, 0);
      return () => clearTimeout(timer);
    }
  }, [recordRenderTime]);

  // Effect for periodic performance updates
  useEffect(() => {
    if (enableMonitoring) {
      const interval = setInterval(debouncedUpdate, 5000); // Update every 5 seconds
      return () => clearInterval(interval);
    }
  }, [enableMonitoring, debouncedUpdate]);

  // Intersection Observer for lazy loading
  const [isVisible, setIsVisible] = useState(false);
  const observerRef = useRef<IntersectionObserver | null>(null);

  useEffect(() => {
    if (componentRef.current) {
      observerRef.current = new IntersectionObserver(
        ([entry]) => {
          setIsVisible(entry.isIntersecting);
        },
        { threshold: 0.1 }
      );

      observerRef.current.observe(componentRef.current);

      return () => {
        if (observerRef.current) {
          observerRef.current.disconnect();
        }
      };
    }
  }, []);

  // Memoization helper
  const memoize = useCallback(<T>(key: string, factory: () => T, dependencies: any[]): T => {
    if (!enableCaching) return factory();

    const cached = getCached<T>(key);
    if (cached) return cached;

    const result = factory();
    setCached(key, result);
    return result;
  }, [enableCaching, getCached, setCached]);

  // Performance measurement helper
  const measurePerformance = useCallback(async <T>(
    operation: string,
    fn: () => Promise<T>
  ): Promise<T> => {
    const startTime = performance.now();
    try {
      const result = await fn();
      const duration = performance.now() - startTime;
      
      if (enableMonitoring) {
        performanceOptimizer.recordApiResponseTime(duration);
      }
      
      return result;
    } catch (error) {
      const duration = performance.now() - startTime;
      
      if (enableMonitoring) {
        performanceOptimizer.recordApiResponseTime(duration);
      }
      
      throw error;
    }
  }, [enableMonitoring]);

  // Batch operations helper
  const batchOperations = useCallback(async <T>(
    operations: Array<() => Promise<T>>,
    batchSize: number = 5
  ): Promise<T[]> => {
    const results: T[] = [];
    
    for (let i = 0; i < operations.length; i += batchSize) {
      const batch = operations.slice(i, i + batchSize);
      const batchResults = await Promise.all(batch.map(op => op()));
      results.push(...batchResults);
    }
    
    return results;
  }, []);

  // Memory usage monitoring
  const [memoryUsage, setMemoryUsage] = useState<number>(0);

  useEffect(() => {
    if (enableMonitoring && 'memory' in performance) {
      const updateMemoryUsage = () => {
        const memory = (performance as any).memory;
        if (memory) {
          setMemoryUsage(memory.usedJSHeapSize);
        }
      };

      const interval = setInterval(updateMemoryUsage, 10000); // Every 10 seconds
      return () => clearInterval(interval);
    }
  }, [enableMonitoring]);

  // Performance warning system
  const [warnings, setWarnings] = useState<string[]>([]);

  useEffect(() => {
    if (!enableMonitoring || !performanceData) return;

    const newWarnings: string[] = [];

    // Check render time
    if (performanceData.renderTime > 100) {
      newWarnings.push(`Slow render time: ${performanceData.renderTime.toFixed(2)}ms`);
    }

    // Check memory usage
    if (memoryUsage > 50 * 1024 * 1024) { // 50MB
      newWarnings.push(`High memory usage: ${(memoryUsage / 1024 / 1024).toFixed(2)}MB`);
    }

    // Check API response time
    if (performanceData.apiMetrics.avgResponseTime > 1000) {
      newWarnings.push(`Slow API response time: ${performanceData.apiMetrics.avgResponseTime.toFixed(2)}ms`);
    }

    setWarnings(newWarnings);
  }, [enableMonitoring, performanceData, memoryUsage]);

  return {
    // Performance monitoring
    isMonitoring,
    startMonitoring,
    stopMonitoring,
    performanceData,
    updatePerformanceData,
    
    // Caching
    getCached,
    setCached,
    clearCache,
    getCacheStats,
    getPerformanceSummary,
    
    // Optimization helpers
    memoize,
    measurePerformance,
    batchOperations,
    
    // Lazy loading
    componentRef,
    isVisible,
    
    // Memory monitoring
    memoryUsage,
    
    // Performance warnings
    warnings,
    
    // Utility functions
    formatMemory: (bytes: number): string => {
      if (bytes < 1024) return `${bytes}B`;
      if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)}KB`;
      if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(2)}MB`;
      return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)}GB`;
    },
    
    formatTime: (ms: number): string => {
      if (ms < 1000) return `${ms.toFixed(2)}ms`;
      if (ms < 60000) return `${(ms / 1000).toFixed(2)}s`;
      return `${(ms / 60000).toFixed(2)}m`;
    }
  };
};

// Utility function for debouncing
function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

export default usePerformanceOptimization;
