import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginForm from './components/LoginForm';
import ETRMDashboard from './components/ETRMDashboard';
import TradingForm from './components/TradingForm';
import RiskDashboard from './pages/RiskDashboard';
import ESGDashboard from './pages/ESGDashboard';
import AdvancedDashboard from './components/AdvancedDashboard';
import GeoRiskDashboard from './components/GeoRiskDashboard';
import QuantumOptimizationDashboard from './components/QuantumOptimizationDashboard';
import CarbonNFTDashboard from './components/CarbonNFTDashboard';
import ComplianceDashboard from './components/ComplianceDashboard';
import ProductionDashboard from './components/ProductionDashboard';
import './App.css';

// API utilities
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check authentication status
    const token = localStorage.getItem('auth_token');
    if (token) {
      // Verify token with backend
      fetch(`${API_BASE_URL}/dashboard`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      .then(response => {
        if (response.ok) {
          return response.json();
        }
        throw new Error('Authentication failed');
      })
      .then(data => {
        setUser(data.user);
        setIsAuthenticated(true);
      })
      .catch(error => {
        console.error('Auth check failed:', error);
        localStorage.removeItem('auth_token');
        setIsAuthenticated(false);
      })
      .finally(() => {
        setLoading(false);
      });
    } else {
      setLoading(false);
    }
  }, []);

  const handleLogin = async (credentials) => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('auth_token', data.access_token);
        setIsAuthenticated(true);
        return { success: true };
      } else {
        const error = await response.json();
        return { success: false, error: error.detail };
      }
    } catch (error) {
      return { success: false, error: 'Network error' };
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    setIsAuthenticated(false);
    setUser(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
              QuantaEnergi ETRM
            </h2>
            <p className="mt-2 text-sm text-gray-600">
              Next-Gen Energy Trading & Risk Management
            </p>
          </div>
          <LoginForm onLogin={handleLogin} />
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Navigation Header */}
        <nav className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <h1 className="text-xl font-semibold text-gray-900">QuantaEnergi</h1>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-600">
                  Welcome, {user?.username || 'Trader'}
                </span>
                <button
                  onClick={handleLogout}
                  className="text-sm text-gray-600 hover:text-gray-900"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<ETRMDashboard />} />
          <Route path="/trading" element={<TradingForm />} />
          <Route path="/risk" element={<RiskDashboard />} />
          <Route path="/esg" element={<ESGDashboard />} />
          <Route path="/geo-risk" element={<GeoRiskDashboard />} />
          <Route path="/quantum" element={<QuantumOptimizationDashboard />} />
          <Route path="/blockchain" element={<CarbonNFTDashboard />} />
          <Route path="/compliance" element={<ComplianceDashboard />} />
          <Route path="/production" element={<ProductionDashboard />} />
          <Route path="/advanced" element={<AdvancedDashboard />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;