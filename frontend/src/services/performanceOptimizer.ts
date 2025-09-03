/**
 * Performance Optimization Service for QuantaEnergi Frontend
 * Provides caching, request batching, and performance monitoring
 */

// Performance monitoring interface
interface PerformanceMetrics {
  apiResponseTime: number;
  cacheHitRate: number;
  memoryUsage: number;
  renderTime: number;
  timestamp: number;
}

// Cache configuration
interface CacheConfig {
  maxSize: number;
  ttl: number; // Time to live in milliseconds
  enableCompression: boolean;
}

// Request batching configuration
interface BatchConfig {
  maxBatchSize: number;
  maxWaitTime: number; // Maximum wait time before executing batch
  enableRetry: boolean;
  maxRetries: number;
}

class PerformanceOptimizer {
  private cache: Map<string, { data: any; timestamp: number; ttl: number }>;
  private batchQueue: Map<string, Array<{ resolve: Function; reject: Function; params: any }>>;
  private performanceMetrics: PerformanceMetrics[];
  private cacheConfig: CacheConfig;
  private batchConfig: BatchConfig;
  private isMonitoring: boolean = false;

  constructor() {
    this.cache = new Map();
    this.batchQueue = new Map();
    this.performanceMetrics = [];
    
    this.cacheConfig = {
      maxSize: 1000,
      ttl: 5 * 60 * 1000, // 5 minutes
      enableCompression: true
    };
    
    this.batchConfig = {
      maxBatchSize: 10,
      maxWaitTime: 100, // 100ms
      enableRetry: true,
      maxRetries: 3
    };

    // Start cache cleanup interval
    this.startCacheCleanup();
  }

  // ============================================================================
  // CACHING SYSTEM
  // ============================================================================

  /**
   * Set cache configuration
   */
  setCacheConfig(config: Partial<CacheConfig>): void {
    this.cacheConfig = { ...this.cacheConfig, ...config };
  }

  /**
   * Get cached data
   */
  getCached<T>(key: string): T | null {
    const cached = this.cache.get(key);
    if (!cached) return null;

    const now = Date.now();
    if (now - cached.timestamp > cached.ttl) {
      this.cache.delete(key);
      return null;
    }

    this.recordCacheHit();
    return cached.data as T;
  }

  /**
   * Set cached data
   */
  setCached<T>(key: string, data: T, ttl?: number): void {
    // Check cache size limit
    if (this.cache.size >= this.cacheConfig.maxSize) {
      this.evictOldestCache();
    }

    const cacheEntry = {
      data,
      timestamp: Date.now(),
      ttl: ttl || this.cacheConfig.ttl
    };

    this.cache.set(key, cacheEntry);
  }

  /**
   * Clear cache
   */
  clearCache(): void {
    this.cache.clear();
  }

  /**
   * Get cache statistics
   */
  getCacheStats(): { size: number; hitRate: number; memoryUsage: number } {
    const totalRequests = this.performanceMetrics.length;
    const cacheHits = this.performanceMetrics.filter(m => m.cacheHitRate > 0).length;
    const hitRate = totalRequests > 0 ? (cacheHits / totalRequests) * 100 : 0;

    return {
      size: this.cache.size,
      hitRate,
      memoryUsage: this.getMemoryUsage()
    };
  }

  // ============================================================================
  // REQUEST BATCHING
  // ============================================================================

  /**
   * Set batch configuration
   */
  setBatchConfig(config: Partial<BatchConfig>): void {
    this.batchConfig = { ...this.batchConfig, ...config };
  }

  /**
   * Add request to batch queue
   */
  async addToBatch<T>(
    batchKey: string,
    requestFn: (params: any[]) => Promise<T[]>,
    params: any
  ): Promise<T> {
    return new Promise((resolve, reject) => {
      if (!this.batchQueue.has(batchKey)) {
        this.batchQueue.set(batchKey, []);
        
        // Schedule batch execution
        setTimeout(() => {
          this.executeBatch(batchKey, requestFn);
        }, this.batchConfig.maxWaitTime);
      }

      const batch = this.batchQueue.get(batchKey)!;
      batch.push({ resolve, reject, params });

      // Execute batch if it reaches max size
      if (batch.length >= this.batchConfig.maxBatchSize) {
        this.executeBatch(batchKey, requestFn);
      }
    });
  }

  /**
   * Execute batched requests
   */
  private async executeBatch<T>(
    batchKey: string,
    requestFn: (params: any[]) => Promise<T[]>
  ): Promise<void> {
    const batch = this.batchQueue.get(batchKey);
    if (!batch || batch.length === 0) return;

    this.batchQueue.delete(batchKey);

    try {
      const allParams = batch.map(item => item.params);
      const results = await this.executeWithRetry(() => requestFn(allParams));

      // Distribute results to individual promises
      batch.forEach((item, index) => {
        if (results[index] !== undefined) {
          item.resolve(results[index]);
        } else {
          item.reject(new Error('Batch execution failed'));
        }
      });
    } catch (error) {
      // Reject all promises in batch
      batch.forEach(item => item.reject(error));
    }
  }

  /**
   * Execute function with retry logic
   */
  private async executeWithRetry<T>(
    fn: () => Promise<T>,
    retryCount: number = 0
  ): Promise<T> {
    try {
      return await fn();
    } catch (error) {
      if (this.batchConfig.enableRetry && retryCount < this.batchConfig.maxRetries) {
        await this.delay(Math.pow(2, retryCount) * 1000); // Exponential backoff
        return this.executeWithRetry(fn, retryCount + 1);
      }
      throw error;
    }
  }

  // ============================================================================
  // PERFORMANCE MONITORING
  // ============================================================================

  /**
   * Start performance monitoring
   */
  startMonitoring(): void {
    this.isMonitoring = true;
    this.performanceMetrics = [];
    
    // Monitor memory usage
    if ('memory' in performance) {
      setInterval(() => {
        this.recordMemoryUsage();
      }, 10000); // Every 10 seconds
    }
  }

  /**
   * Stop performance monitoring
   */
  stopMonitoring(): void {
    this.isMonitoring = false;
  }

  /**
   * Record API response time
   */
  recordApiResponseTime(responseTime: number): void {
    if (!this.isMonitoring) return;

    this.performanceMetrics.push({
      apiResponseTime: responseTime,
      cacheHitRate: 0,
      memoryUsage: this.getMemoryUsage(),
      renderTime: 0,
      timestamp: Date.now()
    });

    // Keep only last 1000 metrics
    if (this.performanceMetrics.length > 1000) {
      this.performanceMetrics = this.performanceMetrics.slice(-1000);
    }
  }

  /**
   * Record cache hit
   */
  private recordCacheHit(): void {
    if (!this.isMonitoring) return;

    const lastMetric = this.performanceMetrics[this.performanceMetrics.length - 1];
    if (lastMetric) {
      lastMetric.cacheHitRate = 1;
    }
  }

  /**
   * Record render time
   */
  recordRenderTime(renderTime: number): void {
    if (!this.isMonitoring) return;

    const lastMetric = this.performanceMetrics[this.performanceMetrics.length - 1];
    if (lastMetric) {
      lastMetric.renderTime = renderTime;
    }
  }

  /**
   * Get performance metrics
   */
  getPerformanceMetrics(): PerformanceMetrics[] {
    return [...this.performanceMetrics];
  }

  /**
   * Get performance summary
   */
  getPerformanceSummary(): {
    avgApiResponseTime: number;
    avgCacheHitRate: number;
    avgRenderTime: number;
    totalRequests: number;
  } {
    if (this.performanceMetrics.length === 0) {
      return {
        avgApiResponseTime: 0,
        avgCacheHitRate: 0,
        avgRenderTime: 0,
        totalRequests: 0
      };
    }

    const totalRequests = this.performanceMetrics.length;
    const avgApiResponseTime = this.performanceMetrics.reduce((sum, m) => sum + m.apiResponseTime, 0) / totalRequests;
    const avgCacheHitRate = this.performanceMetrics.reduce((sum, m) => sum + m.cacheHitRate, 0) / totalRequests;
    const avgRenderTime = this.performanceMetrics.reduce((sum, m) => sum + m.renderTime, 0) / totalRequests;

    return {
      avgApiResponseTime,
      avgCacheHitRate,
      avgRenderTime,
      totalRequests
    };
  }

  // ============================================================================
  // UTILITY METHODS
  // ============================================================================

  /**
   * Get memory usage
   */
  private getMemoryUsage(): number {
    if ('memory' in performance) {
      return (performance as any).memory.usedJSHeapSize;
    }
    return 0;
  }

  /**
   * Record memory usage
   */
  private recordMemoryUsage(): void {
    if (!this.isMonitoring) return;

    const lastMetric = this.performanceMetrics[this.performanceMetrics.length - 1];
    if (lastMetric) {
      lastMetric.memoryUsage = this.getMemoryUsage();
    }
  }

  /**
   * Evict oldest cache entries
   */
  private evictOldestCache(): void {
    const entries = Array.from(this.cache.entries());
    entries.sort((a, b) => a[1].timestamp - b[1].timestamp);
    
    // Remove oldest 20% of entries
    const removeCount = Math.ceil(entries.length * 0.2);
    for (let i = 0; i < removeCount; i++) {
      this.cache.delete(entries[i][0]);
    }
  }

  /**
   * Start cache cleanup interval
   */
  private startCacheCleanup(): void {
    setInterval(() => {
      const now = Date.now();
      for (const [key, entry] of this.cache.entries()) {
        if (now - entry.timestamp > entry.ttl) {
          this.cache.delete(key);
        }
      }
    }, 60000); // Every minute
  }

  /**
   * Delay utility
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Generate cache key from parameters
   */
  generateCacheKey(prefix: string, params: Record<string, any>): string {
    const sortedParams = Object.keys(params)
      .sort()
      .map(key => `${key}:${params[key]}`)
      .join('|');
    
    return `${prefix}:${sortedParams}`;
  }

  /**
   * Compress data for storage
   */
  private compressData(data: any): string {
    if (this.cacheConfig.enableCompression) {
      return JSON.stringify(data);
    }
    return data;
  }

  /**
   * Decompress data from storage
   */
  private decompressData(data: string): any {
    if (this.cacheConfig.enableCompression) {
      try {
        return JSON.parse(data);
      } catch {
        return data;
      }
    }
    return data;
  }
}

// Create singleton instance
const performanceOptimizer = new PerformanceOptimizer();

// Export the instance and class
export default performanceOptimizer;
export { PerformanceOptimizer, type PerformanceMetrics, type CacheConfig, type BatchConfig };
