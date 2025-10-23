import React, { Suspense, lazy, useState, useEffect } from 'react';
import usePerformanceOptimization from '../hooks/usePerformanceOptimization';

interface LazyLoadWrapperProps {
  component: React.ComponentType<any>;
  fallback?: React.ReactNode;
  threshold?: number;
  rootMargin?: string;
  enableCaching?: boolean;
  cacheKey?: string;
  ttl?: number;
  props?: Record<string, any>;
}

const LazyLoadWrapper: React.FC<LazyLoadWrapperProps> = ({
  component: Component,
  fallback = <div className="animate-pulse bg-gray-200 h-32 rounded-lg"></div>,
  threshold = 0.1,
  rootMargin = '50px',
  enableCaching = true,
  cacheKey,
  ttl = 5 * 60 * 1000, // 5 minutes
  props = {}
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [shouldLoad, setShouldLoad] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const {
    componentRef,
    isVisible,
    memoize,
    setCached,
    getCached,
    formatMemory,
    formatTime
  } = usePerformanceOptimization({
    enableCaching,
    cacheKey,
    ttl,
    recordRenderTime: true
  });

  // Lazy load the component when it becomes visible
  useEffect(() => {
    if (isVisible && !isLoaded && !shouldLoad) {
      setShouldLoad(true);
    }
  }, [isVisible, isLoaded, shouldLoad]);

  // Load component data from cache or fetch
  useEffect(() => {
    if (!shouldLoad) return;

    const loadComponent = async () => {
      try {
        // Check cache first
        if (enableCaching && cacheKey) {
          const cached = getCached(cacheKey);
          if (cached) {
            setIsLoaded(true);
            return;
          }
        }

        // Simulate component loading delay
        await new Promise(resolve => setTimeout(resolve, 100));

        // Cache the loaded state
        if (enableCaching && cacheKey) {
          setCached(cacheKey, { loaded: true }, ttl);
        }

        setIsLoaded(true);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to load component'));
      }
    };

    loadComponent();
  }, [shouldLoad, enableCaching, cacheKey, ttl, getCached, setCached]);

  // Error boundary
  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Component Load Error</h3>
            <p className="text-sm text-red-700 mt-1">{error.message}</p>
            <button
              onClick={() => {
                setError(null);
                setIsLoaded(false);
                setShouldLoad(false);
              }}
              className="mt-2 text-sm text-red-600 hover:text-red-500 font-medium"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Show fallback while loading
  if (!isLoaded) {
    return (
      <div ref={componentRef} className="w-full">
        {fallback}
        {enableCaching && cacheKey && (
          <div className="mt-2 text-xs text-gray-500">
            <span className="inline-flex items-center">
              <svg className="animate-spin -ml-1 mr-2 h-3 w-3 text-gray-400" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Loading component...
            </span>
          </div>
        )}
      </div>
    );
  }

  // Render the component
  return (
    <div ref={componentRef} className="w-full">
      <Suspense fallback={fallback}>
        <Component {...props} />
      </Suspense>
    </div>
  );
};

export default LazyLoadWrapper;
