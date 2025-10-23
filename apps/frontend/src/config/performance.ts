/**
 * Performance Optimization Configuration
 * Centralized configuration for all performance-related settings
 */

export interface PerformanceConfig {
  // Caching configuration
  caching: {
    enabled: boolean;
    defaultTTL: number; // milliseconds
    maxSize: number;
    enableCompression: boolean;
    compressionThreshold: number; // bytes
  };

  // Request batching configuration
  batching: {
    enabled: boolean;
    maxBatchSize: number;
    maxWaitTime: number; // milliseconds
    enableRetry: boolean;
    maxRetries: number;
    retryDelay: number; // milliseconds
  };

  // Performance monitoring configuration
  monitoring: {
    enabled: boolean;
    updateInterval: number; // milliseconds
    recordRenderTime: boolean;
    recordMemoryUsage: boolean;
    recordApiResponseTime: boolean;
    maxMetricsHistory: number;
  };

  // Lazy loading configuration
  lazyLoading: {
    enabled: boolean;
    threshold: number;
    rootMargin: string;
    fallbackDelay: number; // milliseconds
  };

  // Memory management configuration
  memory: {
    enableMonitoring: boolean;
    warningThreshold: number; // bytes
    criticalThreshold: number; // bytes
    cleanupInterval: number; // milliseconds
  };

  // API optimization configuration
  api: {
    enableCaching: boolean;
    cacheTTL: number; // milliseconds
    enableRequestBatching: boolean;
    enableRetry: boolean;
    timeout: number; // milliseconds
    maxConcurrentRequests: number;
  };

  // Component optimization configuration
  components: {
    enableMemoization: boolean;
    enableLazyLoading: boolean;
    enableIntersectionObserver: boolean;
    renderTimeThreshold: number; // milliseconds
  };
}

// Default performance configuration
export const defaultPerformanceConfig: PerformanceConfig = {
  caching: {
    enabled: true,
    defaultTTL: 5 * 60 * 1000, // 5 minutes
    maxSize: 1000,
    enableCompression: true,
    compressionThreshold: 1024 // 1KB
  },

  batching: {
    enabled: true,
    maxBatchSize: 10,
    maxWaitTime: 100, // 100ms
    enableRetry: true,
    maxRetries: 3,
    retryDelay: 1000 // 1 second
  },

  monitoring: {
    enabled: true,
    updateInterval: 5000, // 5 seconds
    recordRenderTime: true,
    recordMemoryUsage: true,
    recordApiResponseTime: true,
    maxMetricsHistory: 1000
  },

  lazyLoading: {
    enabled: true,
    threshold: 0.1,
    rootMargin: '50px',
    fallbackDelay: 100 // 100ms
  },

  memory: {
    enableMonitoring: true,
    warningThreshold: 50 * 1024 * 1024, // 50MB
    criticalThreshold: 100 * 1024 * 1024, // 100MB
    cleanupInterval: 30000 // 30 seconds
  },

  api: {
    enableCaching: true,
    cacheTTL: 5 * 60 * 1000, // 5 minutes
    enableRequestBatching: true,
    enableRetry: true,
    timeout: 30000, // 30 seconds
    maxConcurrentRequests: 10
  },

  components: {
    enableMemoization: true,
    enableLazyLoading: true,
    enableIntersectionObserver: true,
    renderTimeThreshold: 100 // 100ms
  }
};

// Environment-specific configurations
export const getPerformanceConfig = (): PerformanceConfig => {
  const env = process.env.NODE_ENV;
  
  switch (env) {
    case 'development':
      return {
        ...defaultPerformanceConfig,
        monitoring: {
          ...defaultPerformanceConfig.monitoring,
          updateInterval: 2000, // More frequent updates in development
          maxMetricsHistory: 500 // Smaller history in development
        },
        caching: {
          ...defaultPerformanceConfig.caching,
          maxSize: 500 // Smaller cache in development
        }
      };

    case 'production':
      return {
        ...defaultPerformanceConfig,
        monitoring: {
          ...defaultPerformanceConfig.monitoring,
          updateInterval: 10000, // Less frequent updates in production
          maxMetricsHistory: 2000 // Larger history in production
        },
        caching: {
          ...defaultPerformanceConfig.caching,
          maxSize: 2000, // Larger cache in production
          defaultTTL: 10 * 60 * 1000 // 10 minutes in production
        },
        api: {
          ...defaultPerformanceConfig.api,
          cacheTTL: 10 * 60 * 1000, // 10 minutes in production
          maxConcurrentRequests: 20 // More concurrent requests in production
        }
      };

    case 'test':
      return {
        ...defaultPerformanceConfig,
        monitoring: {
          ...defaultPerformanceConfig.monitoring,
          enabled: false // Disable monitoring in tests
        },
        caching: {
          ...defaultPerformanceConfig.caching,
          enabled: false // Disable caching in tests
        }
      };

    default:
      return defaultPerformanceConfig;
  }
};

// Performance optimization presets
export const performancePresets = {
  // High performance preset for critical applications
  highPerformance: {
    caching: {
      enabled: true,
      defaultTTL: 15 * 60 * 1000, // 15 minutes
      maxSize: 5000,
      enableCompression: true
    },
    batching: {
      enabled: true,
      maxBatchSize: 20,
      maxWaitTime: 50 // 50ms
    },
    monitoring: {
      updateInterval: 2000, // 2 seconds
      maxMetricsHistory: 5000
    }
  },

  // Memory efficient preset for resource-constrained environments
  memoryEfficient: {
    caching: {
      enabled: true,
      defaultTTL: 2 * 60 * 1000, // 2 minutes
      maxSize: 500,
      enableCompression: true
    },
    batching: {
      enabled: true,
      maxBatchSize: 5,
      maxWaitTime: 200 // 200ms
    },
    monitoring: {
      updateInterval: 10000, // 10 seconds
      maxMetricsHistory: 500
    }
  },

  // Balanced preset for general use
  balanced: defaultPerformanceConfig
};

// Utility functions for configuration management
export const updatePerformanceConfig = (
  currentConfig: PerformanceConfig,
  updates: Partial<PerformanceConfig>
): PerformanceConfig => {
  return {
    ...currentConfig,
    ...updates,
    caching: { ...currentConfig.caching, ...updates.caching },
    batching: { ...currentConfig.batching, ...updates.batching },
    monitoring: { ...currentConfig.monitoring, ...updates.monitoring },
    lazyLoading: { ...currentConfig.lazyLoading, ...updates.lazyLoading },
    memory: { ...currentConfig.memory, ...updates.memory },
    api: { ...currentConfig.api, ...updates.api },
    components: { ...currentConfig.components, ...updates.components }
  };
};

export const validatePerformanceConfig = (config: PerformanceConfig): string[] => {
  const errors: string[] = [];

  // Validate caching configuration
  if (config.caching.maxSize <= 0) {
    errors.push('Cache max size must be positive');
  }
  if (config.caching.defaultTTL <= 0) {
    errors.push('Cache TTL must be positive');
  }

  // Validate batching configuration
  if (config.batching.maxBatchSize <= 0) {
    errors.push('Batch max size must be positive');
  }
  if (config.batching.maxWaitTime <= 0) {
    errors.push('Batch wait time must be positive');
  }

  // Validate monitoring configuration
  if (config.monitoring.updateInterval <= 0) {
    errors.push('Monitoring update interval must be positive');
  }
  if (config.monitoring.maxMetricsHistory <= 0) {
    errors.push('Max metrics history must be positive');
  }

  // Validate memory configuration
  if (config.memory.warningThreshold >= config.memory.criticalThreshold) {
    errors.push('Warning threshold must be less than critical threshold');
  }

  // Validate API configuration
  if (config.api.timeout <= 0) {
    errors.push('API timeout must be positive');
  }
  if (config.api.maxConcurrentRequests <= 0) {
    errors.push('Max concurrent requests must be positive');
  }

  return errors;
};

// Export the current configuration
export const currentPerformanceConfig = getPerformanceConfig();

export default currentPerformanceConfig;
