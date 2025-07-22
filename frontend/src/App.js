import React, { useState, useEffect, Suspense, lazy } from 'react';
import { openDatabase } from 'react-native-sqlite-storage';
const PriceDisplayLazy = lazy(() => import('./components/PriceDisplay'));
const AnalyticsDashboard = lazy(() => import('./components/AnalyticsDashboard'));
const GamifiedHub = lazy(() => import('./components/GamifiedHub'));
const MarketplaceMockup = lazy(() => import('./components/MarketplaceMockup'));
function App() {
  const [language, setLanguage] = useState('en');
  const [isOffline, setIsOffline] = useState(!navigator.onLine);
  const db = openDatabase({ name: 'offline.db' }, () => {}, error => console.log(error));
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
    <div className={min-h-screen bg-gray-200 p-4 } dir={language === 'ar' ? 'rtl' : 'ltr'} lang={language}>
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
