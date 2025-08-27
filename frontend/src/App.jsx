import React, { useState, useEffect, Suspense, lazy } from 'react';
const PriceDisplayLazy = lazy(() => import('./components/PriceDisplay.jsx'));
const AnalyticsDashboard = lazy(() => import('./components/AnalyticsDashboard.jsx'));
const GamifiedHub = lazy(() => import('./components/GamifiedHub.jsx'));
const MarketplaceMockup = lazy(() => import('./components/MarketplaceMockup.jsx'));
function App() {
  const [language, setLanguage] = useState('en');
  const [isOffline, setIsOffline] = useState(!navigator.onLine);
  // Database initialization removed for web compatibility
  useEffect(() => {
    const handleOffline = () => setIsOffline(true);
    const handleOnline = () => setIsOffline(false);
    window.addEventListener('offline', handleOffline);
    window.addEventListener('online', handleOnline);
    return () => {
      window.removeEventListener('offline', handleOffline);
      window.removeEventListener('online', handleOnline);
    };
  }, [isOffline]);
  return (
    <div className="min-h-screen bg-gray-200 p-4" dir={language === 'ar' ? 'rtl' : 'ltr'} lang={language}>
      <select onChange={e => setLanguage(e.target.value)}>
        <option value="en">English</option>
        <option value="ar">Arabic</option>
        <option value="fr">French</option>
      </select>
      {isOffline ? <div>Offline Mode</div> : (
        <Suspense fallback={<div>Loading...</div>}>
          <PriceDisplayLazy />
          <AnalyticsDashboard />
          <GamifiedHub />
          <MarketplaceMockup />
        </Suspense>
      )}
    </div>
  );
}
export default App;
