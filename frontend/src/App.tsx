import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import TradeForm from './components/TradeForm';
import RiskDashboard from './pages/RiskDashboard';
import ESGDashboard from './pages/ESGDashboard';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<TradeForm />} />
        <Route path="/risk" element={<RiskDashboard />} />
        <Route path="/esg" element={<ESGDashboard />} />
      </Routes>
    </Router>
  );
}

export default App;