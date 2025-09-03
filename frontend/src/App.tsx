import React from 'react';
import { PerformanceProvider } from './contexts/PerformanceContext';
import MainDashboard from './components/MainDashboard';
import './App.css';

function App() {
  return (
    <PerformanceProvider autoStart={true} updateInterval={5000}>
      <div className="App">
        <MainDashboard userId="user123" />
      </div>
    </PerformanceProvider>
  );
}

export default App;
