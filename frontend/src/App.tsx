import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import TradeForm from './components/TradeForm';
import RiskDashboard from './pages/RiskDashboard';
import ESGDashboard from './pages/ESGDashboard';
import AdvancedDashboard from './components/AdvancedDashboard';
import GeoRiskDashboard from './components/GeoRiskDashboard';
import QuantumOptimizationDashboard from './components/QuantumOptimizationDashboard';
import CarbonNFTDashboard from './components/CarbonNFTDashboard';
import ComplianceDashboard from './components/ComplianceDashboard';
import ProductionDashboard from './components/ProductionDashboard';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<TradeForm />} />
        <Route path="/risk" element={<RiskDashboard />} />
        <Route path="/esg" element={<ESGDashboard />} />
        <Route path="/dashboard" element={<AdvancedDashboard />} />
        <Route path="/geo-risk" element={<GeoRiskDashboard />} />
        <Route path="/quantum" element={<QuantumOptimizationDashboard />} />
        <Route path="/blockchain" element={<CarbonNFTDashboard />} />
        <Route path="/compliance" element={<ComplianceDashboard />} />
        <Route path="/production" element={<ProductionDashboard />} />
      </Routes>
    </Router>
  );
}

export default App;